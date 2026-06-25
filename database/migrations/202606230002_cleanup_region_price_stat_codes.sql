delete from public.region_price_stat
where (region_level = 'SIDO' and region_code !~ '^[0-9]{2}$')
   or (region_level = 'SIGUNGU' and region_code !~ '^[0-9]{5}$')
   or (region_level = 'DONG' and region_code !~ '^[0-9]{5}:.+$');
