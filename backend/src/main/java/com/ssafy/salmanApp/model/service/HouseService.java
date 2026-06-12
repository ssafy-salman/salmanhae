package com.ssafy.salmanApp.model.service;

import java.util.List;
import com.ssafy.salmanApp.model.dto.HouseInfoDTO;
import com.ssafy.salmanApp.model.dto.HouseDealDTO;

public interface HouseService {
    void insertHouseInfo(HouseInfoDTO houseInfo) throws Exception;
    HouseInfoDTO getHouseInfoByAptSeq(String aptSeq) throws Exception;
    void updateHouseInfo(HouseInfoDTO houseInfo) throws Exception;
    void deleteHouseInfo(String aptSeq) throws Exception;
    List<HouseInfoDTO> getAllHouseInfos() throws Exception;
    List<HouseInfoDTO> getHouseInfosBySggCd(String sggCd) throws Exception;
    List<HouseInfoDTO> getHouseInfosByUmdCd(String umdCd) throws Exception;
    List<HouseInfoDTO> getHouseInfosByAptNm(String aptNm) throws Exception;

    void insertHouseDeal(HouseDealDTO houseDeal) throws Exception;
    HouseDealDTO getHouseDealByNo(int no) throws Exception;
    void updateHouseDeal(HouseDealDTO houseDeal) throws Exception;
    void deleteHouseDeal(int no) throws Exception;
    List<HouseDealDTO> getAllHouseDeals() throws Exception;
    List<HouseDealDTO> getHouseDealsByAptSeq(String aptSeq) throws Exception;
    List<HouseDealDTO> getHouseDealsByDealYear(int dealYear) throws Exception;
    List<HouseDealDTO> getHouseDealsByYearAndMonth(int dealYear, int dealMonth) throws Exception;
}