package com.ssafy.salmanhae.service.safety.ingest;

import java.io.ByteArrayInputStream;
import java.math.BigDecimal;
import java.net.URI;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.DocumentBuilderFactory;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.util.UriComponentsBuilder;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import com.ssafy.salmanhae.config.SafetyDataProperties;
import com.ssafy.salmanhae.model.dto.safety.SafetyFacilityType;

@Component
@ConditionalOnProperty(name = "safety.data.safemap-police-enabled", havingValue = "true")
public class SafemapPoliceFacilityClient implements SafetyFacilitySourceClient {

	static final String SOURCE = "IF_0036";

	private static final Logger log = LoggerFactory.getLogger(SafemapPoliceFacilityClient.class);

	private final SafetyDataProperties properties;
	private final RestClient restClient;

	public SafemapPoliceFacilityClient(SafetyDataProperties properties, RestClient.Builder restClientBuilder) {
		this.properties = properties;
		this.restClient = SafetyFacilityHttpSupport.restClient(restClientBuilder);
	}

	@Override
	public String sourceName() {
		return SOURCE;
	}

	@Override
	public List<NormalizedSafetyFacility> fetchFacilities() {
		List<NormalizedSafetyFacility> facilities = new ArrayList<>();
		int pageNo = 1;
		int maxPages = properties.maxPages();
		while (pageNo <= maxPages) {
			URI uri = UriComponentsBuilder.fromUriString(properties.safemapPoliceUrl())
					.queryParam("serviceKey", encodedQueryParam(properties.safemapServiceKey()))
					.queryParam("pageNo", pageNo)
					.queryParam("numOfRows", properties.pageSize())
					.queryParam("returnType", "xml")
					.build(true)
					.toUri();
			String body;
			try {
				body = restClient.get().uri(uri).retrieve().body(String.class);
			} catch (RuntimeException exception) {
				log.warn("Failed to fetch Safemap police safety facilities from {}", properties.safemapPoliceUrl(), exception);
				break;
			}
			if (body == null || body.isBlank()) {
				break;
			}
			ParsedSafetyFacilityPage page;
			try {
				page = parsePage(body);
			} catch (IllegalArgumentException exception) {
				log.warn("Failed to parse Safemap police safety facilities", exception);
				break;
			}
			if (page.rawItemCount() == 0) {
				break;
			}
			facilities.addAll(page.facilities());
			if (page.rawItemCount() < properties.pageSize()) {
				break;
			}
			pageNo++;
		}
		if (pageNo > maxPages) {
			log.warn("Stopped fetching Safemap police safety facilities after reaching max page limit {}", maxPages);
		}
		return facilities;
	}

	public List<NormalizedSafetyFacility> parseFacilities(String xml) {
		return parsePage(xml).facilities();
	}

	private ParsedSafetyFacilityPage parsePage(String xml) {
		try {
			DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
			factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
			factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
			factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
			factory.setXIncludeAware(false);
			factory.setExpandEntityReferences(false);

			var documentBuilder = factory.newDocumentBuilder();
			var document = documentBuilder.parse(new ByteArrayInputStream(xml.getBytes(StandardCharsets.UTF_8)));
			NodeList itemNodes = document.getElementsByTagName("item");
			List<NormalizedSafetyFacility> facilities = new ArrayList<>();
			for (int i = 0; i < itemNodes.getLength(); i++) {
				facilities.add(toFacility((Element) itemNodes.item(i)));
			}
			return new ParsedSafetyFacilityPage(
					facilities.stream()
							.filter(NormalizedSafetyFacility::hasUsableCoordinates)
							.toList(),
					itemNodes.getLength()
			);
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

	private String encodedQueryParam(String value) {
		return URLEncoder.encode(value == null ? "" : value, StandardCharsets.UTF_8);
	}
}
