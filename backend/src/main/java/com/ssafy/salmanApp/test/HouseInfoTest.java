package com.ssafy.salmanApp.test;

import java.util.List;
import com.ssafy.salmanApp.model.dto.HouseInfoDTO;
import com.ssafy.salmanApp.model.dto.HouseDealDTO;
import com.ssafy.salmanApp.model.service.BasicHouseService;
import com.ssafy.salmanApp.model.service.HouseService;

public class HouseInfoTest {
    public static void main(String[] args) {
        try {
            HouseService houseService = BasicHouseService.getInstance();

            // ── 전체 목록 조회 ──
            System.out.println("===== 아파트 전체 목록 =====");
            for (HouseInfoDTO h : houseService.getAllHouseInfos()) {
                System.out.println(h);
            }

            // ── aptSeq로 단건 조회 ──
            String testAptSeq = "11110-100";
            HouseInfoDTO fetchedHouse = houseService.getHouseInfoByAptSeq(testAptSeq);
            System.out.println("아파트 단건 조회 : " + fetchedHouse);

            // ── 시군구 코드로 검색 ──
            System.out.println("===== sggCd 11110 검색 =====");
            for (HouseInfoDTO h : houseService.getHouseInfosBySggCd("11110")) {
                System.out.println(h);
            }

            // ── 읍면동 코드로 검색 ──
            System.out.println("===== umdCd 17400 검색 =====");
            for (HouseInfoDTO h : houseService.getHouseInfosByUmdCd("17400")) {
                System.out.println(h);
            }

            // ── 아파트명으로 검색 ──
            System.out.println("===== 아파트명 '경희궁' 검색 =====");
            for (HouseInfoDTO h : houseService.getHouseInfosByAptNm("경희궁")) {
                System.out.println(h);
            }


        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}