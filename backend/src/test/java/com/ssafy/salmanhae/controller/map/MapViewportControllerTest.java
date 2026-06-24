package com.ssafy.salmanhae.controller.map;

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
class MapViewportControllerTest {

	@Autowired
	private MockMvc mockMvc;

	@Test
	void getViewportIsPublicAndReturnsSigunguModeAtWideZoom() throws Exception {
		mockMvc.perform(baseViewportRequest().param("zoom", "11"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.message").value("OK"))
				.andExpect(jsonPath("$.data.mode").value("SIGUNGU_AVG"))
				.andExpect(jsonPath("$.data.totalCount").value(0))
				.andExpect(jsonPath("$.data.items", hasSize(0)));
	}

	@Test
	void getViewportReturnsDongModeAtMiddleZoom() throws Exception {
		mockMvc.perform(baseViewportRequest().param("zoom", "12"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.mode").value("DONG_AVG"));

		mockMvc.perform(baseViewportRequest().param("zoom", "13"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.mode").value("DONG_AVG"));
	}

	@Test
	void getViewportReturnsClusterModeBeforeDetailedMarkers() throws Exception {
		mockMvc.perform(baseViewportRequest().param("zoom", "14"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.mode").value("PROPERTY_CLUSTER"));

		mockMvc.perform(baseViewportRequest().param("zoom", "15"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.mode").value("PROPERTY_CLUSTER"));
	}

	@Test
	void getViewportReturnsPropertyMarkerModeAtDetailedZoom() throws Exception {
		mockMvc.perform(baseViewportRequest().param("zoom", "16"))
				.andExpect(status().isOk())
				.andExpect(jsonPath("$.data.mode").value("PROPERTY_MARKER"));
	}

	@Test
	void getViewportRejectsInvalidBounds() throws Exception {
		mockMvc.perform(get("/api/v1/map/viewport")
						.param("west", "127.00")
						.param("east", "126.00")
						.param("south", "37.46")
						.param("north", "37.48")
						.param("zoom", "12"))
				.andExpect(status().isBadRequest())
				.andExpect(jsonPath("$.code").value("INVALID_BOUNDS"))
				.andExpect(jsonPath("$.status").value(400));
	}

	@Test
	void getViewportRejectsMissingZoom() throws Exception {
		mockMvc.perform(baseViewportRequest())
				.andExpect(status().isBadRequest())
				.andExpect(jsonPath("$.code").value("INVALID_REQUEST"))
				.andExpect(jsonPath("$.status").value(400));
	}

	private org.springframework.test.web.servlet.request.MockHttpServletRequestBuilder baseViewportRequest() {
		return get("/api/v1/map/viewport")
				.param("west", "126.93")
				.param("east", "126.94")
				.param("south", "37.46")
				.param("north", "37.48");
	}
}
