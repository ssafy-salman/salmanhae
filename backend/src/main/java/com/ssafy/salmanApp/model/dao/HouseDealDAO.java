package com.ssafy.salmanApp.model.dao;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;
import com.ssafy.salmanApp.model.dto.HouseDealDTO;

public interface HouseDealDAO {
    void insertHouseDeal(Connection conn, HouseDealDTO houseDeal) throws SQLException;
    HouseDealDTO getHouseDealByNo(Connection conn, int no) throws SQLException;
    void updateHouseDeal(Connection conn, HouseDealDTO houseDeal) throws SQLException;
    void deleteHouseDeal(Connection conn, int no) throws SQLException;
    List<HouseDealDTO> getAllHouseDeals(Connection conn) throws SQLException;
    List<HouseDealDTO> getHouseDealsByAptSeq(Connection conn, String aptSeq) throws SQLException;
    List<HouseDealDTO> getHouseDealsByDealYear(Connection conn, int dealYear) throws SQLException;
    List<HouseDealDTO> getHouseDealsByYearAndMonth(Connection conn, int dealYear, int dealMonth) throws SQLException;
}