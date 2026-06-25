package com.ssafy.salmanhae.controller.property;

import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class PropertyControllerTest {

	@Autowired
	private MockMvc mockMvc;

	@Test
	void searchPropertiesReturnsActivePropertiesInBounds() throws Exception {
		mockMvc.perform(get("/api/v1/properties")
						.param("west", "126.93")
						.param("east", "126.94")
						.param("south", "37.46")
						.param("north", "37.48"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.message").value("OK"))
				.andExpect(jsonPath("$.data.totalCount").value(2))
				.andExpect(jsonPath("$.data.items", hasSize(2)))
				.andExpect(jsonPath("$.data.items[0].id").value(1))
				.andExpect(jsonPath("$.data.items[0].title").value("대학동 그린빌 월세"))
				.andExpect(jsonPath("$.data.items[0].transactionType").value("MONTHLY_RENT"));
	}

	@Test
	void searchPropertiesAppliesTransactionAndPropertyFilters() throws Exception {
		mockMvc.perform(get("/api/v1/properties")
						.param("west", "126.93")
						.param("east", "126.94")
						.param("south", "37.46")
						.param("north", "37.48")
						.param("transactionType", "SALE")
						.param("propertyType", "APARTMENT")
						.param("minPrice", "700000000")
						.param("maxPrice", "750000000"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.totalCount").value(1))
				.andExpect(jsonPath("$.data.items[0].id").value(2))
				.andExpect(jsonPath("$.data.items[0].price").value(720000000));
	}

	@Test
	void searchPropertiesAppliesDepositFilters() throws Exception {
		mockMvc.perform(get("/api/v1/properties")
						.param("west", "126.93")
						.param("east", "126.94")
						.param("south", "37.46")
						.param("north", "37.48")
						.param("minDeposit", "9000000")
						.param("maxDeposit", "11000000"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.totalCount").value(1))
				.andExpect(jsonPath("$.data.items[0].id").value(1))
				.andExpect(jsonPath("$.data.items[0].deposit").value(10000000));
	}

	@Test
	void searchPropertiesAppliesKeywordFilter() throws Exception {
		mockMvc.perform(get("/api/v1/properties")
						.param("west", "126.93")
						.param("east", "126.94")
						.param("south", "37.46")
						.param("north", "37.48")
						.param("keyword", "매매"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.totalCount").value(1))
				.andExpect(jsonPath("$.data.items[0].id").value(2));

		mockMvc.perform(get("/api/v1/properties")
						.param("west", "126.93")
						.param("east", "126.94")
						.param("south", "37.46")
						.param("north", "37.48")
						.param("keyword", "검색결과없음"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.totalCount").value(0))
				.andExpect(jsonPath("$.data.items", hasSize(0)));
	}

	@Test
	void searchPropertiesTreatsKeywordWildcardsAsLiteralText() throws Exception {
		mockMvc.perform(get("/api/v1/properties")
						.param("west", "126.93")
						.param("east", "126.94")
						.param("south", "37.46")
						.param("north", "37.48")
						.param("keyword", "%"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.totalCount").value(0))
				.andExpect(jsonPath("$.data.items", hasSize(0)));

		mockMvc.perform(get("/api/v1/properties")
						.param("west", "126.93")
						.param("east", "126.94")
						.param("south", "37.46")
						.param("north", "37.48")
						.param("keyword", "_"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.totalCount").value(0))
				.andExpect(jsonPath("$.data.items", hasSize(0)));
	}

	@Test
	void searchPropertiesRejectsInvalidBounds() throws Exception {
		mockMvc.perform(get("/api/v1/properties")
						.param("west", "127.00")
						.param("east", "126.00")
						.param("south", "37.46")
						.param("north", "37.48"))
				.andExpect(status().isBadRequest())
				.andExpect(jsonPath("$.code").value("INVALID_BOUNDS"))
				.andExpect(jsonPath("$.status").value(400));
	}

	@Test
	void searchPropertiesRejectsInvalidLatitudeBounds() throws Exception {
		mockMvc.perform(get("/api/v1/properties")
						.param("west", "126.93")
						.param("east", "126.94")
						.param("south", "37.48")
						.param("north", "37.46"))
				.andExpect(status().isBadRequest())
				.andExpect(jsonPath("$.code").value("INVALID_BOUNDS"))
				.andExpect(jsonPath("$.status").value(400));
	}

	@Test
	void searchPropertiesRejectsNegativeFilters() throws Exception {
		mockMvc.perform(get("/api/v1/properties")
						.param("west", "126.93")
						.param("east", "126.94")
						.param("south", "37.46")
						.param("north", "37.48")
						.param("minPrice", "-1"))
				.andExpect(status().isBadRequest())
				.andExpect(jsonPath("$.code").value("INVALID_REQUEST"))
				.andExpect(jsonPath("$.status").value(400));
	}

	@Test
	void getPropertyReturnsActivePropertyDetail() throws Exception {
		mockMvc.perform(get("/api/v1/properties/{propertyId}", 1))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.message").value("OK"))
				.andExpect(jsonPath("$.data.id").value(1))
				.andExpect(jsonPath("$.data.buildingKey").value("1162010200:ONE_ROOM:그린빌:12-3"))
				.andExpect(jsonPath("$.data.maintenanceFee").value(70000))
				.andExpect(jsonPath("$.data.description").value("대학가 인근 원룸입니다."));
	}

	@Test
	void getPropertyReturnsNotFoundForMissingOrInactiveProperty() throws Exception {
		mockMvc.perform(get("/api/v1/properties/{propertyId}", 3))
				.andExpect(status().isNotFound())
				.andExpect(jsonPath("$.code").value("PROPERTY_NOT_FOUND"))
				.andExpect(jsonPath("$.status").value(404));
	}

	@Test
	void getPropertyTransactionsReturnsComparableRows() throws Exception {
		mockMvc.perform(get("/api/v1/properties/{propertyId}/transactions", 1)
						.param("years", "3"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.message").value("OK"))
				.andExpect(jsonPath("$.data.totalCount").value(3))
				.andExpect(jsonPath("$.data.items", hasSize(3)))
				.andExpect(jsonPath("$.data.items[0].contractYearMonth").value("2026-05"))
				.andExpect(jsonPath("$.data.items[0].deposit").value(10000000))
				.andExpect(jsonPath("$.data.items[0].monthlyRent").value(520000))
				.andExpect(jsonPath("$.data.items[0].areaM2").value(21.80));
	}

	@Test
	void getPropertyTransactionsReturnsNotFoundForMissingProperty() throws Exception {
		mockMvc.perform(get("/api/v1/properties/{propertyId}/transactions", 999))
				.andExpect(status().isNotFound())
				.andExpect(jsonPath("$.code").value("PROPERTY_NOT_FOUND"));
	}

	@Test
	void getPropertyTransactionsRejectsInvalidYearsAtController() throws Exception {
		mockMvc.perform(get("/api/v1/properties/{propertyId}/transactions", 1)
						.param("years", "0"))
				.andExpect(status().isBadRequest())
				.andExpect(jsonPath("$.code").value("INVALID_REQUEST"))
				.andExpect(jsonPath("$.status").value(400));
	}

	@Test
	void getPropertySafetySummaryReturnsPrecomputedScore() throws Exception {
		mockMvc.perform(get("/api/v1/properties/{propertyId}/safety-summary", 1)
						.param("radius", "500"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.message").value("OK"))
				.andExpect(jsonPath("$.data.propertyId").value(1))
				.andExpect(jsonPath("$.data.radius").value(500))
				.andExpect(jsonPath("$.data.safetyScore").value(78))
				.andExpect(jsonPath("$.data.priceScore").value(64))
				.andExpect(jsonPath("$.data.cctvCount300m").value(8))
				.andExpect(jsonPath("$.data.bellCount300m").value(2))
				.andExpect(jsonPath("$.data.lightCount300m").value(14))
				.andExpect(jsonPath("$.data.policeCount500m").value(1));
	}

	@Test
	void getPropertySafetySummaryReturnsNotFoundForMissingProperty() throws Exception {
		mockMvc.perform(get("/api/v1/properties/{propertyId}/safety-summary", 999))
				.andExpect(status().isNotFound())
				.andExpect(jsonPath("$.code").value("PROPERTY_NOT_FOUND"));
	}

	@Test
	void getPropertySafetySummaryRejectsUnsupportedRadius() throws Exception {
		mockMvc.perform(get("/api/v1/properties/{propertyId}/safety-summary", 1)
						.param("radius", "400"))
				.andExpect(status().isBadRequest())
				.andExpect(jsonPath("$.code").value("INVALID_REQUEST"))
				.andExpect(jsonPath("$.status").value(400));
	}
}
