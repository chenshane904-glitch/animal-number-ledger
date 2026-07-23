"""测试customtkinter颜色显示"""
import customtkinter as ctk

# 设置浅色主题
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("颜色测试")
app.geometry("400x300")

frame = ctk.CTkFrame(app)
frame.pack(padx=20, pady=20, fill='both', expand=True)

# 测试不同的红色设置方式
label1 = ctk.CTkLabel(frame, text="测试1: red", font=("Arial", 16, "bold"), text_color="red")
label1.pack(pady=10)

label2 = ctk.CTkLabel(frame, text="测试2: #FF0000", font=("Arial", 16, "bold"), text_color="#FF0000")
label2.pack(pady=10)

label3 = ctk.CTkLabel(frame, text="测试3: #ff0000", font=("Arial", 16, "bold"), text_color="#ff0000")
label3.pack(pady=10)

# 带背景的测试
frame2 = ctk.CTkFrame(frame, fg_color="#FFE5E5", border_width=3, border_color="red")
frame2.pack(pady=10, padx=10, fill='x')
label4 = ctk.CTkLabel(frame2, text="测试4: 红色边框+背景", font=("Arial", 16, "bold"), text_color="red")
label4.pack(pady=10)

# 默认颜色
label5 = ctk.CTkLabel(frame, text="测试5: 默认颜色", font=("Arial", 16, "bold"))
label5.pack(pady=10)

app.mainloop()
