package com.ssafy.salmanApp.model.dto;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@ToString
@Setter
@Getter
public class HouseDealDTO {
    private int no;
    private String aptSeq;
    private String aptDong;
    private String floor;
    private int dealYear;
    private int dealMonth;
    private int dealDay;
    private double excluUseAr;
    private String dealAmount;

    public HouseDealDTO() {
        super();
    }

    public HouseDealDTO(int no, String aptSeq, String aptDong, String floor,
                        int dealYear, int dealMonth, int dealDay,
                        double excluUseAr, String dealAmount) {
        super();
        this.no = no;
        this.aptSeq = aptSeq;
        this.aptDong = aptDong;
        this.floor = floor;
        this.dealYear = dealYear;
        this.dealMonth = dealMonth;
        this.dealDay = dealDay;
        this.excluUseAr = excluUseAr;
        this.dealAmount = dealAmount;
    }
}