package com.ssafy.salmanhae.service.safety;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.argThat;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.ssafy.salmanhae.model.dao.safety.SafetyFacilityDao;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityIngestionResult;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;
import com.ssafy.salmanhae.service.safety.ingest.NormalizedSafetyFacility;
import com.ssafy.salmanhae.service.safety.ingest.SafetyFacilitySourceClient;

@ExtendWith(MockitoExtension.class)
class SafetyFacilityIngestionServiceTest {

	@Mock
	private SafetyFacilityDao safetyFacilityDao;

	@Test
	void ingestAllContinuesWhenOneSourceFails() {
		SafetyFacilitySourceClient successfulClient = new FakeSourceClient(
				"SUCCESS_SOURCE",
				List.of(facility("ok-1"))
		);
		SafetyFacilitySourceClient failingClient = new FailingSourceClient("FAIL_SOURCE");
		when(safetyFacilityDao.upsertAll(argThat(rows -> rows != null && rows.size() == 1))).thenReturn(1);
		SafetyFacilityIngestionService service = new SafetyFacilityIngestionServiceImpl(
				List.of(successfulClient, failingClient),
				safetyFacilityDao
		);

		SafetyFacilityIngestionResult result = service.ingestAll();

		assertThat(result.sourceResults()).hasSize(2);
		assertThat(result.sourceResults())
				.extracting(SafetyFacilityIngestionResult.SourceResult::source)
				.containsExactly("SUCCESS_SOURCE", "FAIL_SOURCE");
		assertThat(result.totalFetchedCount()).isEqualTo(1);
		assertThat(result.totalUpsertedCount()).isEqualTo(1);
		assertThat(result.totalFailedCount()).isEqualTo(1);
		assertThat(result.hasFailures()).isTrue();
		verify(safetyFacilityDao).upsertAll(argThat(rows -> rows != null && rows.size() == 1));
	}

	@Test
	void ingestAllCountsSkippedRowsWhenDaoDoesNotPersistEveryFetchedRow() {
		SafetyFacilitySourceClient sourceClient = new FakeSourceClient(
				"CCTV_CSV",
				List.of(facility("cctv-1"), facility("cctv-2"))
		);
		when(safetyFacilityDao.upsertAll(argThat(rows -> rows != null && rows.size() == 2))).thenReturn(1);
		SafetyFacilityIngestionService service = new SafetyFacilityIngestionServiceImpl(
				List.of(sourceClient),
				safetyFacilityDao
		);

		SafetyFacilityIngestionResult result = service.ingestAll();

		SafetyFacilityIngestionResult.SourceResult sourceResult = result.sourceResults().getFirst();
		assertThat(sourceResult.fetchedCount()).isEqualTo(2);
		assertThat(sourceResult.upsertedCount()).isEqualTo(1);
		assertThat(sourceResult.skippedCount()).isEqualTo(1);
		assertThat(sourceResult.failedCount()).isZero();
	}

	private NormalizedSafetyFacility facility(String sourceId) {
		return new NormalizedSafetyFacility(
				SafetyFacilityType.CCTV,
				"Test CCTV",
				"Seoul",
				new BigDecimal("37.4703210"),
				new BigDecimal("126.9361110"),
				"CCTV_CSV",
				sourceId,
				"fixture"
		);
	}

	private record FakeSourceClient(
			String sourceName,
			List<NormalizedSafetyFacility> facilities
	) implements SafetyFacilitySourceClient {

		@Override
		public List<NormalizedSafetyFacility> fetchFacilities() {
			return facilities;
		}
	}

	private record FailingSourceClient(String sourceName) implements SafetyFacilitySourceClient {

		@Override
		public List<NormalizedSafetyFacility> fetchFacilities() {
			throw new IllegalStateException("source failed");
		}
	}
}
