package com.ssafy.salmanhae.model.dto.safety;

import java.util.List;

public record SafetyFacilityIngestionResult(
		List<SourceResult> sourceResults
) {

	public SafetyFacilityIngestionResult {
		sourceResults = sourceResults == null ? List.of() : List.copyOf(sourceResults);
	}

	public int totalFetchedCount() {
		return sourceResults.stream()
				.mapToInt(SourceResult::fetchedCount)
				.sum();
	}

	public int totalUpsertedCount() {
		return sourceResults.stream()
				.mapToInt(SourceResult::upsertedCount)
				.sum();
	}

	public int totalSkippedCount() {
		return sourceResults.stream()
				.mapToInt(SourceResult::skippedCount)
				.sum();
	}

	public int totalFailedCount() {
		return sourceResults.stream()
				.mapToInt(SourceResult::failedCount)
				.sum();
	}

	public boolean hasFailures() {
		return totalFailedCount() > 0;
	}

	public record SourceResult(
			String source,
			int fetchedCount,
			int upsertedCount,
			int skippedCount,
			int failedCount,
			String errorMessage
	) {

		public boolean success() {
			return failedCount == 0;
		}
	}
}
