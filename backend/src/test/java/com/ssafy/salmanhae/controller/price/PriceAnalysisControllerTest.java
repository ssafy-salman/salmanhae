package com.ssafy.salmanhae.controller.price;

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
class PriceAnalysisControllerTest {

	@Autowired
	private MockMvc mockMvc;

	@Test
	void getPriceAnalysisReturnsCachedRegionAndBuildingStats() throws Exception {
		mockMvc.perform(get("/api/v1/price-analysis")
						.param("legalDongCode", "1162010200")
						.param("propertyType", "ONE_ROOM")
						.param("transactionType", "MONTHLY_RENT"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.message").value("OK"))
				.andExpect(jsonPath("$.data.legalDongCode").value("1162010200"))
				.andExpect(jsonPath("$.data.propertyType").value("ONE_ROOM"))
				.andExpect(jsonPath("$.data.transactionType").value("MONTHLY_RENT"))
				.andExpect(jsonPath("$.data.regionStats", hasSize(1)))
				.andExpect(jsonPath("$.data.regionStats[0].regionLevel").value("DONG"))
				.andExpect(jsonPath("$.data.regionStats[0].avgDeposit").value(10500000))
				.andExpect(jsonPath("$.data.regionStats[0].avgMonthlyRent").value(520000))
				.andExpect(jsonPath("$.data.buildingStats", hasSize(1)))
				.andExpect(jsonPath("$.data.buildingStats[0].buildingKey").value("1162010200:ONE_ROOM:그린빌:12-3"))
				.andExpect(jsonPath("$.data.buildingStats[0].medianDeposit").value(11000000));
	}
}
