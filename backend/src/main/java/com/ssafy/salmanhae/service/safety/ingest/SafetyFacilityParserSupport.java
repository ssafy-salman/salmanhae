package com.ssafy.salmanhae.service.safety.ingest;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import com.fasterxml.jackson.databind.JsonNode;

final class SafetyFacilityParserSupport {

	private SafetyFacilityParserSupport() {
	}

	static List<Map<String, String>> parseCsv(String csv) {
		List<String> records = parseCsvRecords(csv);
		if (records.size() < 2) {
			return List.of();
		}
		List<String> headers = parseCsvLine(stripBom(records.get(0)));
		List<Map<String, String>> rows = new ArrayList<>();
		for (int i = 1; i < records.size(); i++) {
			List<String> values = parseCsvLine(records.get(i));
			Map<String, String> row = new HashMap<>();
			for (int j = 0; j < headers.size() && j < values.size(); j++) {
				row.put(normalizeKey(headers.get(j)), values.get(j).trim());
			}
			rows.add(row);
		}
		return rows;
	}

	private static List<String> parseCsvRecords(String csv) {
		if (csv == null || csv.isBlank()) {
			return List.of();
		}
		List<String> records = new ArrayList<>();
		StringBuilder current = new StringBuilder();
		boolean inQuotes = false;
		for (int i = 0; i < csv.length(); i++) {
			char ch = csv.charAt(i);
			if (ch == '"') {
				current.append(ch);
				if (inQuotes && i + 1 < csv.length() && csv.charAt(i + 1) == '"') {
					current.append(csv.charAt(i + 1));
					i++;
				} else {
					inQuotes = !inQuotes;
				}
			} else if ((ch == '\n' || ch == '\r') && !inQuotes) {
				if (ch == '\r' && i + 1 < csv.length() && csv.charAt(i + 1) == '\n') {
					i++;
				}
				addCsvRecord(records, current);
			} else {
				current.append(ch);
			}
		}
		addCsvRecord(records, current);
		return records;
	}

	private static void addCsvRecord(List<String> records, StringBuilder current) {
		String record = current.toString();
		if (!record.isBlank()) {
			records.add(record);
		}
		current.setLength(0);
	}

	static List<String> parseCsvLine(String line) {
		List<String> values = new ArrayList<>();
		StringBuilder current = new StringBuilder();
		boolean inQuotes = false;
		for (int i = 0; i < line.length(); i++) {
			char ch = line.charAt(i);
			if (ch == '"') {
				if (inQuotes && i + 1 < line.length() && line.charAt(i + 1) == '"') {
					current.append('"');
					i++;
				} else {
					inQuotes = !inQuotes;
				}
			} else if (ch == ',' && !inQuotes) {
				values.add(current.toString());
				current.setLength(0);
			} else {
				current.append(ch);
			}
		}
		values.add(current.toString());
		return values;
	}

	static String value(Map<String, String> row, String... keys) {
		for (String key : keys) {
			String value = row.get(normalizeKey(key));
			if (value != null && !value.isBlank()) {
				return value.trim();
			}
		}
		return "";
	}

	static String text(JsonNode node, String... fieldNames) {
		for (String fieldName : fieldNames) {
			JsonNode value = findField(node, fieldName);
			if (value != null && !value.isMissingNode() && !value.isNull()) {
				String text = value.asText("");
				if (!text.isBlank()) {
					return text.trim();
				}
			}
		}
		return "";
	}

	static BigDecimal decimal(String value) {
		if (value == null || value.isBlank()) {
			return null;
		}
		try {
			return new BigDecimal(value.trim());
		} catch (NumberFormatException exception) {
			return null;
		}
	}

	static BigDecimal decimal(JsonNode node, String... fieldNames) {
		return decimal(text(node, fieldNames));
	}

	static boolean isUsableCoordinate(BigDecimal latitude, BigDecimal longitude) {
		return latitude != null && longitude != null
				&& latitude.compareTo(BigDecimal.valueOf(-90)) >= 0
				&& latitude.compareTo(BigDecimal.valueOf(90)) <= 0
				&& longitude.compareTo(BigDecimal.valueOf(-180)) >= 0
				&& longitude.compareTo(BigDecimal.valueOf(180)) <= 0;
	}

	static List<JsonNode> itemNodes(JsonNode root) {
		List<JsonNode> result = new ArrayList<>();
		collectItemNodes(root, result);
		return result;
	}

	static int totalCount(JsonNode root) {
		JsonNode total = findField(root, "totalCount");
		if (total == null) {
			total = findField(root, "total_count");
		}
		return total == null ? -1 : total.asInt(-1);
	}

	static JsonNode findField(JsonNode root, String fieldName) {
		if (root == null || root.isNull()) {
			return null;
		}
		if (root.has(fieldName)) {
			return root.get(fieldName);
		}
		String normalized = normalizeKey(fieldName);
		if (root.isObject()) {
			var fields = root.fields();
			while (fields.hasNext()) {
				var entry = fields.next();
				if (normalizeKey(entry.getKey()).equals(normalized)) {
					return entry.getValue();
				}
				JsonNode nested = findField(entry.getValue(), fieldName);
				if (nested != null) {
					return nested;
				}
			}
		} else if (root.isArray()) {
			for (JsonNode child : root) {
				JsonNode nested = findField(child, fieldName);
				if (nested != null) {
					return nested;
				}
			}
		}
		return null;
	}

	static String normalizeKey(String value) {
		return value == null ? "" : value
				.replace("\uFEFF", "")
				.replaceAll("[\\s_\\-()]", "")
				.toLowerCase(Locale.ROOT);
	}

	private static void collectItemNodes(JsonNode node, List<JsonNode> result) {
		if (node == null || node.isNull()) {
			return;
		}
		if (node.isObject()) {
			var fields = node.fields();
			while (fields.hasNext()) {
				var entry = fields.next();
				String key = normalizeKey(entry.getKey());
				JsonNode value = entry.getValue();
				if (("items".equals(key) || "item".equals(key) || "data".equals(key)) && value.isArray()) {
					value.forEach(result::add);
				} else if ("item".equals(key) && value.isObject()) {
					result.add(value);
				} else {
					collectItemNodes(value, result);
				}
			}
		} else if (node.isArray()) {
			node.forEach(child -> collectItemNodes(child, result));
		}
	}

	private static String stripBom(String value) {
		return value.replace("\uFEFF", "");
	}
}
