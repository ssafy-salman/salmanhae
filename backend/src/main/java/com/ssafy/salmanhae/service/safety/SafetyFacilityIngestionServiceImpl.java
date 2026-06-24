package com.ssafy.salmanhae.service.safety;

import java.util.List;
import java.util.Objects;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import com.ssafy.salmanhae.model.dao.safety.SafetyFacilityDao;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityIngestionResult;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityRow;
import com.ssafy.salmanhae.service.safety.ingest.NormalizedSafetyFacility;
import com.ssafy.salmanhae.service.safety.ingest.SafetyFacilitySourceClient;

@Service
public class SafetyFacilityIngestionServiceImpl implements SafetyFacilityIngestionService {

	private static final Logger log = LoggerFactory.getLogger(SafetyFacilityIngestionServiceImpl.class);

	private final List<SafetyFacilitySourceClient> sourceClients;
	private final SafetyFacilityDao safetyFacilityDao;

	public SafetyFacilityIngestionServiceImpl(
			List<SafetyFacilitySourceClient> sourceClients,
			SafetyFacilityDao safetyFacilityDao
	) {
		this.sourceClients = sourceClients == null ? List.of() : List.copyOf(sourceClients);
		this.safetyFacilityDao = safetyFacilityDao;
	}

	@Override
	public SafetyFacilityIngestionResult ingestAll() {
		List<SafetyFacilityIngestionResult.SourceResult> sourceResults = sourceClients.stream()
				.map(this::ingestSource)
				.toList();
		SafetyFacilityIngestionResult result = new SafetyFacilityIngestionResult(sourceResults);
		log.info(
				"Safety facility ingestion finished: fetched={}, upserted={}, skipped={}, failed={}",
				result.totalFetchedCount(),
				result.totalUpsertedCount(),
				result.totalSkippedCount(),
				result.totalFailedCount()
		);
		return result;
	}

	private SafetyFacilityIngestionResult.SourceResult ingestSource(SafetyFacilitySourceClient sourceClient) {
		String sourceName = sourceClient.sourceName();
		try {
			List<NormalizedSafetyFacility> facilities = safeList(sourceClient.fetchFacilities());
			List<SafetyFacilityRow> rows = facilities.stream()
					.filter(Objects::nonNull)
					.filter(NormalizedSafetyFacility::hasUsableCoordinates)
					.map(NormalizedSafetyFacility::toRow)
					.toList();
			int upsertedCount = rows.isEmpty() ? 0 : safetyFacilityDao.upsertAll(rows);
			int skippedCount = Math.max(0, facilities.size() - upsertedCount);
			log.info(
					"Safety facility source ingested: source={}, fetched={}, upserted={}, skipped={}",
					sourceName,
					facilities.size(),
					upsertedCount,
					skippedCount
			);
			return new SafetyFacilityIngestionResult.SourceResult(
					sourceName,
					facilities.size(),
					upsertedCount,
					skippedCount,
					0,
					null
			);
		} catch (RuntimeException exception) {
			log.warn("Safety facility source ingestion failed: source={}", sourceName, exception);
			return new SafetyFacilityIngestionResult.SourceResult(
					sourceName,
					0,
					0,
					0,
					1,
					exception.getMessage()
			);
		}
	}

	private List<NormalizedSafetyFacility> safeList(List<NormalizedSafetyFacility> facilities) {
		return facilities == null ? List.of() : facilities;
	}
}
