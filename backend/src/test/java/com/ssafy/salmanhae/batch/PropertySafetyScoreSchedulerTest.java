package com.ssafy.salmanhae.batch;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;

import com.ssafy.salmanhae.model.dto.safety.PropertySafetyScoreResult;
import com.ssafy.salmanhae.service.safety.PropertySafetyScoreService;

class PropertySafetyScoreSchedulerTest {

	@Test
	void runMonthlyRecalculationDelegatesToService() {
		PropertySafetyScoreService service = org.mockito.Mockito.mock(PropertySafetyScoreService.class);
		when(service.recalculateAll()).thenReturn(List.of(
				new PropertySafetyScoreResult(1L, 78, 8, 2, 14, 1)
		));
		PropertySafetyScoreScheduler scheduler = new PropertySafetyScoreScheduler(service);

		scheduler.runMonthlyRecalculation();

		verify(service).recalculateAll();
	}
}
