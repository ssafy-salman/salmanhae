package com.ssafy.salmanApp.model.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import com.ssafy.salmanApp.model.dto.HouseInfoDTO;

public class BasicHouseInfoDAO implements HouseInfoDAO {

    private static BasicHouseInfoDAO instance = new BasicHouseInfoDAO();

    private BasicHouseInfoDAO() {}

    public static BasicHouseInfoDAO getInstance() {
        return instance;
    }

    @Override
    public void insertHouseInfo(Connection conn, HouseInfoDTO houseInfo) throws SQLException {
        String sql = "INSERT INTO houseinfos (apt_seq, sgg_cd, umd_cd, umd_nm, jibun, road_nm_sgg_cd, road_nm, road_nm_bonbun, road_nm_bubun, apt_nm, build_year, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, houseInfo.getAptSeq());
            stmt.setString(2, houseInfo.getSggCd());
            stmt.setString(3, houseInfo.getUmdCd());
            stmt.setString(4, houseInfo.getUmdNm());
            stmt.setString(5, houseInfo.getJibun());
            stmt.setString(6, houseInfo.getRoadNmSggCd());
            stmt.setString(7, houseInfo.getRoadNm());
            stmt.setString(8, houseInfo.getRoadNmBonbun());
            stmt.setString(9, houseInfo.getRoadNmBubun());
            stmt.setString(10, houseInfo.getAptNm());
            stmt.setInt(11, houseInfo.getBuildYear());
            stmt.setString(12, houseInfo.getLatitude());
            stmt.setString(13, houseInfo.getLongitude());
            stmt.executeUpdate();
        }
    }

    @Override
    public HouseInfoDTO getHouseInfoByAptSeq(Connection conn, String aptSeq) throws SQLException {
        String sql = "SELECT * FROM houseinfos WHERE apt_seq = ?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, aptSeq);
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    return mapResultSetToHouseInfo(rs);
                }
            }
        }
        return null;
    }

    @Override
    public void updateHouseInfo(Connection conn, HouseInfoDTO houseInfo) throws SQLException {
        String sql = "UPDATE houseinfos SET sgg_cd=?, umd_cd=?, umd_nm=?, jibun=?, road_nm_sgg_cd=?, road_nm=?, road_nm_bonbun=?, road_nm_bubun=?, apt_nm=?, build_year=?, latitude=?, longitude=? WHERE apt_seq=?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, houseInfo.getSggCd());
            stmt.setString(2, houseInfo.getUmdCd());
            stmt.setString(3, houseInfo.getUmdNm());
            stmt.setString(4, houseInfo.getJibun());
            stmt.setString(5, houseInfo.getRoadNmSggCd());
            stmt.setString(6, houseInfo.getRoadNm());
            stmt.setString(7, houseInfo.getRoadNmBonbun());
            stmt.setString(8, houseInfo.getRoadNmBubun());
            stmt.setString(9, houseInfo.getAptNm());
            stmt.setInt(10, houseInfo.getBuildYear());
            stmt.setString(11, houseInfo.getLatitude());
            stmt.setString(12, houseInfo.getLongitude());
            stmt.setString(13, houseInfo.getAptSeq());
            stmt.executeUpdate();
        }
    }

    @Override
    public void deleteHouseInfo(Connection conn, String aptSeq) throws SQLException {
        String sql = "DELETE FROM houseinfos WHERE apt_seq = ?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, aptSeq);
            stmt.executeUpdate();
        }
    }

    @Override
    public List<HouseInfoDTO> getAllHouseInfos(Connection conn) throws SQLException {
        String sql = "SELECT * FROM houseinfos";
        List<HouseInfoDTO> list = new ArrayList<>();
        try (PreparedStatement stmt = conn.prepareStatement(sql);
             ResultSet rs = stmt.executeQuery()) {
            while (rs.next()) {
                list.add(mapResultSetToHouseInfo(rs));
            }
        }
        return list;
    }

    @Override
    public List<HouseInfoDTO> getHouseInfosBySggCd(Connection conn, String sggCd) throws SQLException {
        String sql = "SELECT * FROM houseinfos WHERE sgg_cd = ?";
        List<HouseInfoDTO> list = new ArrayList<>();
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, sggCd);
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    list.add(mapResultSetToHouseInfo(rs));
                }
            }
        }
        return list;
    }

    @Override
    public List<HouseInfoDTO> getHouseInfosByUmdCd(Connection conn, String umdCd) throws SQLException {
        String sql = "SELECT * FROM houseinfos WHERE umd_cd = ?";
        List<HouseInfoDTO> list = new ArrayList<>();
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, umdCd);
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    list.add(mapResultSetToHouseInfo(rs));
                }
            }
        }
        return list;
    }

    @Override
    public List<HouseInfoDTO> getHouseInfosByAptNm(Connection conn, String aptNm) throws SQLException {
        String sql = "SELECT * FROM houseinfos WHERE apt_nm LIKE ?";
        List<HouseInfoDTO> list = new ArrayList<>();
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, "%" + aptNm + "%");
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    list.add(mapResultSetToHouseInfo(rs));
                }
            }
        }
        return list;
    }

    private HouseInfoDTO mapResultSetToHouseInfo(ResultSet rs) throws SQLException {
        return new HouseInfoDTO(
            rs.getString("apt_seq"),
            rs.getString("sgg_cd"),
            rs.getString("umd_cd"),
            rs.getString("umd_nm"),
            rs.getString("jibun"),
            rs.getString("road_nm_sgg_cd"),
            rs.getString("road_nm"),
            rs.getString("road_nm_bonbun"),
            rs.getString("road_nm_bubun"),
            rs.getString("apt_nm"),
            rs.getInt("build_year"),
            rs.getString("latitude"),
            rs.getString("longitude")
        );
    }
}