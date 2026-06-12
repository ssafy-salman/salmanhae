package com.ssafy.salmanApp.model.dto;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@ToString
@Setter
@Getter
public class HouseInfoDTO {
    private String aptSeq;
    private String sggCd;
    private String umdCd;
    private String umdNm;
    private String jibun;
    private String roadNmSggCd;
    private String roadNm;
    private String roadNmBonbun;
    private String roadNmBubun;
    private String aptNm;
    private int buildYear;
    private String latitude;
    private String longitude;

    public HouseInfoDTO() {
        super();
    }

    public HouseInfoDTO(String aptSeq, String sggCd, String umdCd, String umdNm,
                        String jibun, String roadNmSggCd, String roadNm,
                        String roadNmBonbun, String roadNmBubun, String aptNm,
                        int buildYear, String latitude, String longitude) {
        super();
        this.aptSeq = aptSeq;
        this.sggCd = sggCd;
        this.umdCd = umdCd;
        this.umdNm = umdNm;
        this.jibun = jibun;
        this.roadNmSggCd = roadNmSggCd;
        this.roadNm = roadNm;
        this.roadNmBonbun = roadNmBonbun;
        this.roadNmBubun = roadNmBubun;
        this.aptNm = aptNm;
        this.buildYear = buildYear;
        this.latitude = latitude;
        this.longitude = longitude;
    }
}