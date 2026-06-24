package com.ssafy.salmanhae.controller.safety;

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
import org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class SafetyFacilityControllerTest {

	@Autowired
	private MockMvc mockMvc;

	@Test
	void getFacilitiesReturnsStoredFacilitiesInBounds() throws Exception {
		mockMvc.perform(baseRequest())
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.message").value("OK"))
				.andExpect(jsonPath("$.data.totalCount").value(4))
				.andExpect(jsonPath("$.data.items", hasSize(4)))
				.andExpect(jsonPath("$.data.items[0].type").value("CCTV"))
				.andExpect(jsonPath("$.data.items[0].name").value("Test CCTV"))
				.andExpect(jsonPath("$.data.items[0].latitude").value(37.4703210))
				.andExpect(jsonPath("$.data.items[0].longitude").value(126.9361110));
	}

	@Test
	void getFacilitiesFiltersTypes() throws Exception {
		mockMvc.perform(baseRequest().param("types", "CCTV,EMERGENCY_BELL"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.totalCount").value(2))
				.andExpect(jsonPath("$.data.items[0].type").value("CCTV"))
				.andExpect(jsonPath("$.data.items[1].type").value("EMERGENCY_BELL"));
	}

	@Test
	void getFacilitiesReturnsInvalidRequestForUnknownType() throws Exception {
		mockMvc.perform(baseRequest().param("types", "CCTV,UNKNOWN"))
				.andExpect(status().isBadRequest())
				.andExpect(jsonPath("$.code").value("INVALID_REQUEST"));
	}

	@Test
	void getFacilitiesReturnsInvalidBoundsForReversedBounds() throws Exception {
		mockMvc.perform(get("/api/v1/safety/facilities")
						.param("west", "126.9400000")
						.param("east", "126.9300000")
						.param("south", "37.4600000")
						.param("north", "37.4800000"))
				.andExpect(status().isBadRequest())
				.andExpect(jsonPath("$.code").value("INVALID_BOUNDS"));
	}

	@Test
	void getFacilitiesIsPublic() throws Exception {
		mockMvc.perform(baseRequest().param("types", "POLICE"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.totalCount").value(1))
				.andExpect(jsonPath("$.data.items[0].type").value("POLICE"));
	}

	private MockHttpServletRequestBuilder baseRequest() {
		return get("/api/v1/safety/facilities")
				.param("west", "126.9300000")
				.param("east", "126.9400000")
				.param("south", "37.4600000")
				.param("north", "37.4800000");
	}
}
