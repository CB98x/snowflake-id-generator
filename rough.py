department = 9
year = 3
student_number = 21

packed = (department << 8) |  (year << 5) | student_number

print(packed)

# unpack:
extracted_student = packed & ((1 << 5) - 1)
extracted_year = (packed >> 5) & ((1 << 3) - 1)
extracted_department = (packed >> 8) & ((1 << 4) - 1)

print(extracted_department, extracted_year, extracted_student)