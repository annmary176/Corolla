from decision_tree import predict

high_risk_input = {
    "mem_score": 0.12, "mem_risk": 1, "mem_conf": 0.15,
    "logic_score": 0.18, "logic_risk": 1, "logic_conf": 0.20,
    "read_score": 0.10, "read_risk": 1, "read_conf": 0.12,
    "write_score": 0.16, "write_risk": 1, "write_conf": 0.18
}

high_for_adhd = {
    "mem_score": 0.45, "mem_risk": 3, "mem_conf": 0.70,

    "logic_score": 0.40, "logic_risk": 3, "logic_conf": 0.65,

    "read_score": 0.12, "read_risk": 1, "read_conf": 0.20,

    "write_score": 0.14, "write_risk": 1, "write_conf": 0.22
}

final = {
  "mem_score": 0.21,
  "mem_risk": 1,
  "mem_conf": 0.22,

  "logic_score": 0.44,
  "logic_risk": 1,
  "logic_conf": 0.35,

  "read_score": 0.18,
  "read_risk": 1,
  "read_conf": 0.12,

  "write_score": 0.51,
  "write_risk": 0,
  "write_conf": 0.45
}

#print("HIgh risk for all")
#print(predict(high_risk_input))
# print(predict(high_for_adhd))
print(predict(final)) # for df 1