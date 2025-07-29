from stock_vn import StockVNData

credential = {
    "type": "service_account",
    "project_id": "vbroker-1598954857808",
    "dataset_id": "vstock",
    "private_key_id": "96e069bb6054b7d7235c0d0449d47b75fad1bf27",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQC7wdt7a8ROotp9\nnflBBl9fy9tH3cw/+aGYFc3yZK1N+uQuQkNkG2o/aeFHptcfSVRo7sa+wvbs9Sei\niRgl6f6lkQItFU6FfL6OtJoJwCdEZ/YWk9qRrYPWLKHUgjPMnmYvGaBfP7ScXKLk\npBfswWMe9o3bV7F/E814N72Q1i6GHPYEu5KQK3bp8QNSAWjnQSv//jtRkouSZ/8X\nZauovnZ+pqMKePxXXxAqPorSl/rWwixg2lJu6beVcSWPG2ap0JcwJxe0bnBguhqY\nOhXHPEsAT6fv9fH2EQ+v0DyemTnPe8uR98X4SWSKnrWLYDKAg0MTzWnhuaW0NCS8\nFhfXKHl/AgMBAAECggEAKYxcC+NMpRQfonWfTzbgSxwa8bvQs4WDr1p/4PhLa3qu\nHNh3/kKcz9yXyBnQ9/Drt27DVzpglw4nD64jxFwUCEJfB2f0IND6gCzR+39kkRwq\nVlOwpdUOXAozY4nOeaTBuwGCPiGkT4emWk8/phojW5o2yQeOVS8mJEi9b7wdvnpv\n8r4DtBmPrIFVol2YiIe7Ht2e6dm+LP/T+Q4dB9wCwCIE//DLL+U9M9QLIzuX4Lz1\ne8tXuxmirmMBbvEqq6gNce/BVbLYEefDR6d8SV9z2HP5kLDADkFsLi9og8bRcDjO\nRcWARJV+Pl0g7HMOckTUvwmo0NdExoA2spF7DNKLhQKBgQDplK3Gx/yd94+AO3Yw\nNPtxBWko8g/N9rcrG+3vScXEYxyJFMHEKhbmu8J42lxAJr87wXHyeu52LPX/SzwZ\npcfYELFTtFxkwv9IbEhAReBu/r0zrk1HGt229LAagqUJEqNtqqlB+b3cbW+yF4Gz\nhRTW2jGpS+1nK5RNr/kWxxazQwKBgQDNxz9LJh03ixti8uZuir6eStwkpL+YjVSm\nLVVdmODoVRbmuahxPi0gOYzm8A5qDjuL4KTr0hm+nUHzb86AuxUyx6Mb8anHQP0K\nKCdSLQxMIlZtgGpZ3kE46T1586XvSGqP1MsqWLLdGkp75Ec6WpAF9/P2alGzfe+r\nFGgaYSBXFQKBgQDVm4cT2z20xHlx/m7GBR3QrO8PZ9Z2N2IoxUDhbKi0QSMOZXIR\nz5/j398noCFu9UA7CFwJMMy0O8e3cPkER2wrtpBECRPZfc3xUDz+sihduQ4TnhnD\npdkOgFQv2jvMwUO9fa2NzTMIyvezePW+0zxMg3uY4/u2Ns9IAF6dqvGiewKBgQCX\nfv4pHFlcQAycj4l4jqsBrMlgLO5lqH9OjIeRjfDe+24N1Veeb5EXbWc/yjJCgFH0\njCG/AAI2JF6ek4zrl1Bm/zUlaIh/CmiApsk0JbgtAQayPV2O5iMMfCLneqqKfLz/\nQUGF3qFoSGfXyFtsKapoyoCQxPt7ctcVE8QEz8bYdQKBgQDOU62ZR/OdECKguaU0\nRWteJ1I5u+8RU/04rIaaBo5NqHoonv4pqB4iq+e9uDMGK4AAUBLpE2/R0KWPFtAa\nMjd48+CaxGo96uWUU8cPKC8mzEF5/GVSQz/v49AWDALi68F3gxQKdnxNanq8li5V\nvZJqCY98BMj6PqPp2OSE8CMFxQ==\n-----END PRIVATE KEY-----\n",
    "client_email": "phongvu2010@vbroker-1598954857808.iam.gserviceaccount.com",
    "client_id": "107839992914545296961",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/phongvu2010%40vbroker-1598954857808.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# stock = StockVNData(symbol="VIC", source="yfinance")
# stock = StockVNData(symbol="VIC", source="TCBS")
stock = StockVNData(symbol="VIC", source="BigQuery", credential=credential)

# df = stock.fetch_data()
df = stock.fetch_data(start="2023-01-01", end="2025-10-01", interval="B")

print(df)
