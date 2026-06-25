package com.ssafy.salmanhae.model.dao.auth;

import com.ssafy.salmanhae.model.dto.auth.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserDao {
    User findByEmail(String email);
    void save(User user);
}
