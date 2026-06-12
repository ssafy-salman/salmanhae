package com.ssafy.salmanApp.test;

import java.util.List;
import com.ssafy.salmanApp.model.dto.HouseDealDTO;
import com.ssafy.salmanApp.model.service.BasicHouseService;
import com.ssafy.salmanApp.model.service.HouseService;

public class HouseDealTest {
    public static void main(String[] args) {
        try {
            HouseService houseService = BasicHouseService.getInstance();

            // ── 전체 거래 목록 조회 ──
            System.out.println("===== 거래 전체 목록 =====");
            for (HouseDealDTO d : houseService.getAllHouseDeals()) {
                System.out.println(d);
            }

            // ── no로 단건 조회 ──
            int testNo = 1; // 실제 DB에 있는 no로 변경
            HouseDealDTO fetchedDeal = houseService.getHouseDealByNo(testNo);
            System.out.println("거래 단건 조회 : " + fetchedDeal);

            // ── aptSeq로 거래 목록 조회 ──
            System.out.println("===== aptSeq로 거래 검색 =====");
            for (HouseDealDTO d : houseService.getHouseDealsByAptSeq("11110-100")) {
                System.out.println(d);
            }

            // ── 연도로 거래 검색 ──
            System.out.println("===== 2011년 거래 목록 =====");
            for (HouseDealDTO d : houseService.getHouseDealsByDealYear(2011)) {
                System.out.println(d);
            }

            // ── 연도+월로 거래 검색 ──
            System.out.println("===== 2011년 11월 거래 목록 =====");
            for (HouseDealDTO d : houseService.getHouseDealsByYearAndMonth(2011, 11)) {
                System.out.println(d);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}