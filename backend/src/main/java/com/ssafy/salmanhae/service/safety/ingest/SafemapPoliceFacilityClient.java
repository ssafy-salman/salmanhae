package com.ssafy.salmanhae.service.safety.ingest;

import java.io.ByteArrayInputStream;
import java.math.BigDecimal;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.DocumentBuilderFactory;

import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import com.ssafy.salmanhae.config.SafetyDataProperties;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@Component
public class SafemapPoliceFacilityClient implements SafetyFacilitySourceClient {

	static final String SOURCE = "IF_0036";

	private final SafetyDataProperties properties;
	private final RestClient restClient;

	public SafemapPoliceFacilityClient(SafetyDataProperties properties, RestClient.Builder restClientBuilder) {
		this.properties = properties;
		this.restClient = restClientBuilder.build();
	}

	@Override
	public String sourceName() {
		return SOURCE;
	}

	@Override
	public List<NormalizedSafetyFacility> fetchFacilities() {
		List<NormalizedSafetyFacility> facilities = new ArrayList<>();
		int pageNo = 1;
		while (true) {
			URI uri = UriComponentsBuilder.fromUriString(properties.safemapPoliceUrl())
					.queryParam("serviceKey", properties.safemapServiceKey())
					.queryParam("pageNo", pageNo)
					.queryParam("numOfRows", properties.pageSize())
					.queryParam("returnType", "xml")
					.build(true)
					.toUri();
			List<NormalizedSafetyFacility> page = parseFacilities(
					restClient.get().uri(uri).retrieve().body(String.class)
			);
			if (page.isEmpty()) {
				break;
			}
			facilities.addAll(page);
			if (page.size() < properties.pageSize()) {
				break;
			}
			pageNo++;
		}
		return facilities;
	}

	public List<NormalizedSafetyFacility> parseFacilities(String xml) {
		try {
			var documentBuilder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
			var document = documentBuilder.parse(new ByteArrayInputStream(xml.getBytes(StandardCharsets.UTF_8)));
			NodeList itemNodes = document.getElementsByTagName("item");
			List<NormalizedSafetyFacility> facilities = new ArrayList<>();
			for (int i = 0; i < itemNodes.getLength(); i++) {
				facilities.add(toFacility((Element) itemNodes.item(i)));
			}
			return facilities.stream()
					.filter(NormalizedSafetyFacility::hasUsableCoordinates)
					.toList();
		} catch (Exception exception) {
			throw new IllegalArgumentException("Invalid Safemap police facility XML payload", exception);
		}
	}

	private NormalizedSafetyFacility toFacility(Element item) {
		BigDecimal longitude = SafetyFacilityParserSupport.decimal(text(item, "x"));
		BigDecimal latitude = SafetyFacilityParserSupport.decimal(text(item, "y"));
		String sourceId = text(item, "objt_id");
		String name = firstNonBlank(text(item, "fclty_nm"), "치안시설");
		if (sourceId.isBlank()) {
			sourceId = name + ":" + latitude + ":" + longitude;
		}
		return new NormalizedSafetyFacility(
				SafetyFacilityType.POLICE,
				name,
				firstNonBlank(text(item, "rn_adres"), text(item, "adres")),
				latitude,
				longitude,
				SOURCE,
				sourceId,
				firstNonBlank(text(item, "fclty_ty"), text(item, "fclty_cd"))
		);
	}

	private String text(Element item, String tagName) {
		NodeList nodes = item.getElementsByTagName(tagName);
		if (nodes.getLength() == 0 || nodes.item(0) == null || nodes.item(0).getTextContent() == null) {
			return "";
		}
		return nodes.item(0).getTextContent().trim();
	}

	private String firstNonBlank(String... values) {
		for (String value : values) {
			if (value != null && !value.isBlank()) {
				return value;
			}
		}
		return "";
	}
}
