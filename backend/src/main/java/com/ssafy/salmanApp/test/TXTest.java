package com.ssafy.salmanApp.test;

import com.ssafy.salmanApp.model.dto.HouseDealDTO;
import com.ssafy.salmanApp.model.service.BasicHouseService;
import com.ssafy.salmanApp.model.service.HouseService;

// 트랜잭션 테스트 - 거래 insert 후 rollback 확인
public class TXTest {
    public static void main(String[] args) {
        try {
            HouseService houseService = BasicHouseService.getInstance();

            HouseDealDTO newDeal = new HouseDealDTO();
            newDeal.setAptSeq("11680-1234"); // 실제 DB에 있는 apt_seq로 변경
            newDeal.setAptDong("101");
            newDeal.setFloor("5");
            newDeal.setDealYear(2024);
            newDeal.setDealMonth(6);
            newDeal.setDealDay(1);
            newDeal.setExcluUseAr(84.92);
            newDeal.setDealAmount("130,000");

            houseService.insertHouseDeal(newDeal);
            System.out.println("거래 등록 성공 - no: " + newDeal.getNo());

        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("거래 등록 실패 - 트랜잭션 롤백");
        }
    }
}