package com.ssafy.salmanApp.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

public class DBUtil {
    private static final String URL = "jdbc:mysql://localhost:3306/ssafy_home";
    //     private static final String URL = "jdbc:mysql://localhost:3306/your_database?useUnicode=true&characterEncoding=UTF-8&serverTimezone=UTC";
    
    private static final String USER = "ssafy";
    private static final String PASSWORD = "ssafy";

    static {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            throw new RuntimeException("MySQL JDBC Driver not found", e);
        }
    } // jdbc4.0 이후 부터 생략 가능 : DriverManager.getConnection시에 드라이버라이브러리의  /META-INF/services/java.sql.Driver 파일 안에 들어있는 드라이버구현클래스의이름 읽어서 자동로딩처리함!
      // 실행하는 환경에서 드라이버 로딩을 어떤식으로 처리하는지 다를 수 있다고 함
      // 따라서, 명시적 로딩 권장!
    
    public static Connection getConnection() throws SQLException {
        Properties properties = new Properties();
        properties.setProperty("user", USER);
        properties.setProperty("password", PASSWORD);
        properties.setProperty("profileSQL", "true");
        return DriverManager.getConnection(URL, properties);
    }
    
    public static void close(AutoCloseable... closeables) {
    	for (AutoCloseable res : closeables) {
			try {
				res.close();
			} catch (Exception e) {
				e.printStackTrace();
			}
		}
    }
}