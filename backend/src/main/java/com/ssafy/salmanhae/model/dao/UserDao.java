package com.ssafy.salmanhae.model.dao;

import com.ssafy.salmanhae.model.dto.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserDao {
    User findByEmail(String email);
    void save(User user);
}
