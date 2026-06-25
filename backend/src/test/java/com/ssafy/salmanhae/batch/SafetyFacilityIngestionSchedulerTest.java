package com.ssafy.salmanhae.batch;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityIngestionResult;
import com.ssafy.salmanhae.service.safety.SafetyFacilityIngestionService;

@ExtendWith(MockitoExtension.class)
class SafetyFacilityIngestionSchedulerTest {

	@Mock
	private SafetyFacilityIngestionService safetyFacilityIngestionService;

	@Test
	void runMonthlyIngestionDelegatesToService() {
		when(safetyFacilityIngestionService.ingestAll())
				.thenReturn(new SafetyFacilityIngestionResult(List.of()));
		SafetyFacilityIngestionScheduler scheduler =
				new SafetyFacilityIngestionScheduler(safetyFacilityIngestionService);

		scheduler.runMonthlyIngestion();

		verify(safetyFacilityIngestionService).ingestAll();
	}
}
