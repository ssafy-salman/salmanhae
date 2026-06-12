package com.ssafy.salmanApp.model.service;

import java.sql.Connection;
import java.util.List;

import com.ssafy.salmanApp.model.dao.BasicHouseDealDAO;
import com.ssafy.salmanApp.model.dao.BasicHouseInfoDAO;
import com.ssafy.salmanApp.model.dao.HouseDealDAO;
import com.ssafy.salmanApp.model.dao.HouseInfoDAO;
import com.ssafy.salmanApp.model.dto.HouseDealDTO;
import com.ssafy.salmanApp.model.dto.HouseInfoDTO;
import com.ssafy.salmanApp.util.DBUtil;

public class BasicHouseService implements HouseService {

    private static BasicHouseService instance = new BasicHouseService();
    private HouseInfoDAO houseInfoDAO = BasicHouseInfoDAO.getInstance();
    private HouseDealDAO houseDealDAO = BasicHouseDealDAO.getInstance();

    private BasicHouseService() {}

    public static BasicHouseService getInstance() {
        return instance;
    }

    // ──────────────────────────────────────
    // HouseInfo
    // ──────────────────────────────────────

    @Override
    public void insertHouseInfo(HouseInfoDTO houseInfo) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            conn.setAutoCommit(false);
            houseInfoDAO.insertHouseInfo(conn, houseInfo);
            conn.commit();
        } catch (Exception e) {
            e.printStackTrace();
            if (conn != null) conn.rollback();
            throw e;
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public HouseInfoDTO getHouseInfoByAptSeq(String aptSeq) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseInfoDAO.getHouseInfoByAptSeq(conn, aptSeq);
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public void updateHouseInfo(HouseInfoDTO houseInfo) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            conn.setAutoCommit(false);
            houseInfoDAO.updateHouseInfo(conn, houseInfo);
            conn.commit();
        } catch (Exception e) {
            e.printStackTrace();
            if (conn != null) conn.rollback();
            throw e;
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public void deleteHouseInfo(String aptSeq) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            conn.setAutoCommit(false);
            // 아파트 삭제 시 연관된 거래 내역도 함께 삭제
            List<HouseDealDTO> deals = houseDealDAO.getHouseDealsByAptSeq(conn, aptSeq);
            for (HouseDealDTO deal : deals) {
                houseDealDAO.deleteHouseDeal(conn, deal.getNo());
            }
            houseInfoDAO.deleteHouseInfo(conn, aptSeq);
            conn.commit();
        } catch (Exception e) {
            e.printStackTrace();
            if (conn != null) conn.rollback();
            throw e;
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public List<HouseInfoDTO> getAllHouseInfos() throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseInfoDAO.getAllHouseInfos(conn);
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public List<HouseInfoDTO> getHouseInfosBySggCd(String sggCd) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseInfoDAO.getHouseInfosBySggCd(conn, sggCd);
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public List<HouseInfoDTO> getHouseInfosByUmdCd(String umdCd) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseInfoDAO.getHouseInfosByUmdCd(conn, umdCd);
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public List<HouseInfoDTO> getHouseInfosByAptNm(String aptNm) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseInfoDAO.getHouseInfosByAptNm(conn, aptNm);
        } finally {
            DBUtil.close(conn);
        }
    }

    // ──────────────────────────────────────
    // HouseDeal
    // ──────────────────────────────────────

    @Override
    public void insertHouseDeal(HouseDealDTO houseDeal) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            conn.setAutoCommit(false);
            houseDealDAO.insertHouseDeal(conn, houseDeal);
            conn.commit();
        } catch (Exception e) {
            e.printStackTrace();
            if (conn != null) conn.rollback();
            throw e;
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public HouseDealDTO getHouseDealByNo(int no) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseDealDAO.getHouseDealByNo(conn, no);
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public void updateHouseDeal(HouseDealDTO houseDeal) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            conn.setAutoCommit(false);
            houseDealDAO.updateHouseDeal(conn, houseDeal);
            conn.commit();
        } catch (Exception e) {
            e.printStackTrace();
            if (conn != null) conn.rollback();
            throw e;
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public void deleteHouseDeal(int no) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            conn.setAutoCommit(false);
            houseDealDAO.deleteHouseDeal(conn, no);
            conn.commit();
        } catch (Exception e) {
            e.printStackTrace();
            if (conn != null) conn.rollback();
            throw e;
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public List<HouseDealDTO> getAllHouseDeals() throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseDealDAO.getAllHouseDeals(conn);
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public List<HouseDealDTO> getHouseDealsByAptSeq(String aptSeq) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseDealDAO.getHouseDealsByAptSeq(conn, aptSeq);
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public List<HouseDealDTO> getHouseDealsByDealYear(int dealYear) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseDealDAO.getHouseDealsByDealYear(conn, dealYear);
        } finally {
            DBUtil.close(conn);
        }
    }

    @Override
    public List<HouseDealDTO> getHouseDealsByYearAndMonth(int dealYear, int dealMonth) throws Exception {
        Connection conn = DBUtil.getConnection();
        try {
            return houseDealDAO.getHouseDealsByYearAndMonth(conn, dealYear, dealMonth);
        } finally {
            DBUtil.close(conn);
        }
    }
}