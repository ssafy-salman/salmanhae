package com.ssafy.salmanhae.batch;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityIngestionResult;
import com.ssafy.salmanhae.service.safety.SafetyFacilityIngestionService;

@Component
@ConditionalOnProperty(
		prefix = "safety.ingestion.scheduler",
		name = "enabled",
		havingValue = "true"
)
public class SafetyFacilityIngestionScheduler {

	private static final Logger log = LoggerFactory.getLogger(SafetyFacilityIngestionScheduler.class);

	private final SafetyFacilityIngestionService safetyFacilityIngestionService;

	public SafetyFacilityIngestionScheduler(SafetyFacilityIngestionService safetyFacilityIngestionService) {
		this.safetyFacilityIngestionService = safetyFacilityIngestionService;
	}

	@Scheduled(
			cron = "${safety.ingestion.scheduler.cron:0 0 3 1 * *}",
			zone = "${safety.ingestion.scheduler.zone:Asia/Seoul}"
	)
	public void runMonthlyIngestion() {
		SafetyFacilityIngestionResult result = safetyFacilityIngestionService.ingestAll();
		log.info(
				"Monthly safety facility ingestion completed: sources={}, fetched={}, upserted={}, skipped={}, failed={}",
				result.sourceResults().size(),
				result.totalFetchedCount(),
				result.totalUpsertedCount(),
				result.totalSkippedCount(),
				result.totalFailedCount()
		);
	}
}
