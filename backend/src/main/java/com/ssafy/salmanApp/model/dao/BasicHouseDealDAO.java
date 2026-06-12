package com.ssafy.salmanApp.model.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import com.ssafy.salmanApp.model.dto.HouseDealDTO;

public class BasicHouseDealDAO implements HouseDealDAO {

    private static BasicHouseDealDAO instance = new BasicHouseDealDAO();

    private BasicHouseDealDAO() {}

    public static BasicHouseDealDAO getInstance() {
        return instance;
    }

    @Override
    public void insertHouseDeal(Connection conn, HouseDealDTO houseDeal) throws SQLException {
        String sql = "INSERT INTO housedeals (apt_seq, apt_dong, floor, deal_year, deal_month, deal_day, exclu_use_ar, deal_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
        try (PreparedStatement stmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            stmt.setString(1, houseDeal.getAptSeq());
            stmt.setString(2, houseDeal.getAptDong());
            stmt.setString(3, houseDeal.getFloor());
            stmt.setInt(4, houseDeal.getDealYear());
            stmt.setInt(5, houseDeal.getDealMonth());
            stmt.setInt(6, houseDeal.getDealDay());
            stmt.setDouble(7, houseDeal.getExcluUseAr());
            stmt.setString(8, houseDeal.getDealAmount());
            stmt.executeUpdate();
            ResultSet generatedKeys = stmt.getGeneratedKeys();
            if (generatedKeys.next()) {
                houseDeal.setNo(generatedKeys.getInt(1));
            }
        }
    }

    @Override
    public HouseDealDTO getHouseDealByNo(Connection conn, int no) throws SQLException {
        String sql = "SELECT * FROM housedeals WHERE no = ?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, no);
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    return mapResultSetToHouseDeal(rs);
                }
            }
        }
        return null;
    }

    @Override
    public void updateHouseDeal(Connection conn, HouseDealDTO houseDeal) throws SQLException {
        String sql = "UPDATE housedeals SET apt_seq=?, apt_dong=?, floor=?, deal_year=?, deal_month=?, deal_day=?, exclu_use_ar=?, deal_amount=? WHERE no=?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, houseDeal.getAptSeq());
            stmt.setString(2, houseDeal.getAptDong());
            stmt.setString(3, houseDeal.getFloor());
            stmt.setInt(4, houseDeal.getDealYear());
            stmt.setInt(5, houseDeal.getDealMonth());
            stmt.setInt(6, houseDeal.getDealDay());
            stmt.setDouble(7, houseDeal.getExcluUseAr());
            stmt.setString(8, houseDeal.getDealAmount());
            stmt.setInt(9, houseDeal.getNo());
            stmt.executeUpdate();
        }
    }

    @Override
    public void deleteHouseDeal(Connection conn, int no) throws SQLException {
        String sql = "DELETE FROM housedeals WHERE no = ?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, no);
            stmt.executeUpdate();
        }
    }

    @Override
    public List<HouseDealDTO> getAllHouseDeals(Connection conn) throws SQLException {
        String sql = "SELECT * FROM housedeals";
        List<HouseDealDTO> list = new ArrayList<>();
        try (PreparedStatement stmt = conn.prepareStatement(sql);
             ResultSet rs = stmt.executeQuery()) {
            while (rs.next()) {
                list.add(mapResultSetToHouseDeal(rs));
            }
        }
        return list;
    }

    @Override
    public List<HouseDealDTO> getHouseDealsByAptSeq(Connection conn, String aptSeq) throws SQLException {
        String sql = "SELECT * FROM housedeals WHERE apt_seq = ?";
        List<HouseDealDTO> list = new ArrayList<>();
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, aptSeq);
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    list.add(mapResultSetToHouseDeal(rs));
                }
            }
        }
        return list;
    }

    @Override
    public List<HouseDealDTO> getHouseDealsByDealYear(Connection conn, int dealYear) throws SQLException {
        String sql = "SELECT * FROM housedeals WHERE deal_year = ?";
        List<HouseDealDTO> list = new ArrayList<>();
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, dealYear);
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    list.add(mapResultSetToHouseDeal(rs));
                }
            }
        }
        return list;
    }

    @Override
    public List<HouseDealDTO> getHouseDealsByYearAndMonth(Connection conn, int dealYear, int dealMonth) throws SQLException {
        String sql = "SELECT * FROM housedeals WHERE deal_year = ? AND deal_month = ?";
        List<HouseDealDTO> list = new ArrayList<>();
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, dealYear);
            stmt.setInt(2, dealMonth);
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    list.add(mapResultSetToHouseDeal(rs));
                }
            }
        }
        return list;
    }

    private HouseDealDTO mapResultSetToHouseDeal(ResultSet rs) throws SQLException {
        return new HouseDealDTO(
            rs.getInt("no"),
            rs.getString("apt_seq"),
            rs.getString("apt_dong"),
            rs.getString("floor"),
            rs.getInt("deal_year"),
            rs.getInt("deal_month"),
            rs.getInt("deal_day"),
            rs.getDouble("exclu_use_ar"),
            rs.getString("deal_amount")
        );
    }
}