package com.ssafy.salmanhae;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@EnableScheduling
@SpringBootApplication
public class SalmanhaeApplication {

	public static void main(String[] args) {
		SpringApplication.run(SalmanhaeApplication.class, args);
	}

}
