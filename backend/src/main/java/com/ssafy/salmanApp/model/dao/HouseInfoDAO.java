package com.ssafy.salmanApp.model.dao;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;
import com.ssafy.salmanApp.model.dto.HouseInfoDTO;

public interface HouseInfoDAO {
    void insertHouseInfo(Connection conn, HouseInfoDTO houseInfo) throws SQLException;
    HouseInfoDTO getHouseInfoByAptSeq(Connection conn, String aptSeq) throws SQLException;
    void updateHouseInfo(Connection conn, HouseInfoDTO houseInfo) throws SQLException;
    void deleteHouseInfo(Connection conn, String aptSeq) throws SQLException;
    List<HouseInfoDTO> getAllHouseInfos(Connection conn) throws SQLException;
    List<HouseInfoDTO> getHouseInfosBySggCd(Connection conn, String sggCd) throws SQLException;
    List<HouseInfoDTO> getHouseInfosByUmdCd(Connection conn, String umdCd) throws SQLException;
    List<HouseInfoDTO> getHouseInfosByAptNm(Connection conn, String aptNm) throws SQLException;
}