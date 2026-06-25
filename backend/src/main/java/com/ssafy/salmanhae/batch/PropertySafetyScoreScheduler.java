package com.ssafy.salmanhae.batch;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreResult;
import com.ssafy.salmanhae.service.safety.PropertySafetyScoreService;

@Component
@ConditionalOnProperty(
		prefix = "safety.score.scheduler",
		name = "enabled",
		havingValue = "true"
)
public class PropertySafetyScoreScheduler {

	private static final Logger log = LoggerFactory.getLogger(PropertySafetyScoreScheduler.class);

	private final PropertySafetyScoreService propertySafetyScoreService;

	public PropertySafetyScoreScheduler(PropertySafetyScoreService propertySafetyScoreService) {
		this.propertySafetyScoreService = propertySafetyScoreService;
	}

	@Scheduled(
			cron = "${safety.score.scheduler.cron:0 30 3 1 * *}",
			zone = "${safety.score.scheduler.zone:Asia/Seoul}"
	)
	public void runMonthlyRecalculation() {
		List<PropertySafetyScoreResult> results = propertySafetyScoreService.recalculateAll();
		log.info("Monthly property safety score recalculation completed: properties={}", results.size());
	}
}
