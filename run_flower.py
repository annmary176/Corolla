from petal_memory import predict_mem

result = predict_mem([
        0.92,  # recall_accuracy
        2.1,   # response_time (seconds)
        5,     # sequence_length
        1      # error_count
    ])

print(result)