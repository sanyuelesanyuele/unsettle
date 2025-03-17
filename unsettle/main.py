import tkinter as tk
from PIL import Image,ImageTk
from tkinter import ttk,messagebox
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os


class JewelryDesigner:
    def __init__(self, root):
        self.root = root
        self.root.title("珠宝设计游戏")
        self.sender_email = "2909011953@qq.com"  # 发送邮箱
        self.receiver_email = "redbeansn@163.com"  # 接收邮箱
        

        # 初始化素材路径
        self.background_image_path = "background.png"  # 自定义背景图路径
        self.material_folder = "materials"             # 素材库文件夹路径

        # 添加撤销/重做状态变量
        self.history = []
        self.current_step = -1
        self.max_history = 50  # 最大历史记录数
        
         # 状态变量
        self.selected_material = None
        self.canvas_elements = []
        self.dragging_item = None

        #添加设计状态控制
        self.is_designing = False

        #添加材料价格字典
        self.material_prices = {
            "gem1.png":5,
        }
        
        # 初始化界面
        self.create_widgets()
        self.load_materials()
        

    def show_delivery_form(self):
        """显示寄送信息表单"""
        delivery_window = tk.Toplevel(self.root)
        delivery_window.title("填写收货信息")
        delivery_window.geometry("300x250")  # 增加窗口高度
        
        # 创建表单
        ttk.Label(delivery_window, text="收件人姓名:").pack(pady=5)
        name_entry = ttk.Entry(delivery_window)
        name_entry.pack(pady=5)
        
        ttk.Label(delivery_window, text="收货地址:").pack(pady=5)
        address_entry = ttk.Entry(delivery_window)
        address_entry.pack(pady=5)
        
        ttk.Label(delivery_window, text="联系电话:").pack(pady=5)
        phone_entry = ttk.Entry(delivery_window)
        phone_entry.pack(pady=5)
        
        def submit_form():
            # 获取表单数据
            name = name_entry.get()
            address = address_entry.get()
            phone = phone_entry.get()
            
            # 验证表单数据
            if not (name and address and phone):
                messagebox.showerror("错误", "请填写所有信息")
                return
            
            # 确认订单
            if messagebox.askyesno("确认订单", "是否确认订单并付款？"):
                # 准备订单信息
                order_info = self.prepare_order_info(name, address, phone)
                # 发送邮件
                if self.send_order_email(order_info):
                    messagebox.showinfo("成功", "订单已确认，付款成功！\n订单信息已发送至商家邮箱。")
                    delivery_window.destroy()
                else:
                    messagebox.showerror("错误", "订单提交失败，请稍后重试")
            else:
                if messagebox.askyesno("取消订单", "确定要取消订单吗？"):
                    delivery_window.destroy()
        
        # 提交按钮
        ttk.Button(delivery_window, text="提交订单", command=submit_form).pack(pady=10)
        ttk.Button(delivery_window, text="取消", command=delivery_window.destroy).pack(pady=5)

    def prepare_order_info(self, name, address, phone):
        """准备订单信息"""
        # 计算总价
        total_price = 10
        materials_used = []
        for elem in self.canvas_elements:
            material_name = os.path.basename(elem["path"])
            if material_name in self.material_prices:
                total_price += self.material_prices[material_name]
                materials_used.append(material_name)

        # 格式化订单信息
        order_info = f"""
新订单通知！

客户信息：
-----------------
姓名：{name}
电话：{phone}
地址：{address}

订单详情：
-----------------
使用材料：{', '.join(materials_used)}
基础价格：10元
材料费用：{total_price - 10}元
总价格：{total_price}元

订单状态：已付款
        """
        return order_info

    def send_order_email(self, order_info):
        """发送订单邮件"""
        try:
            # 邮件服务器配置
            smtp_server = "smtp.qq.com"  # QQ邮箱服务器
            smtp_port = 587  # 安全连接端口
            sender = self.sender_email  # 发件人邮箱
            password = "xxmnintctxlddcij"    # 邮箱授权码

            # 创建邮件内容
            message = MIMEText(order_info, 'plain', 'utf-8')
            message['Subject'] = Header('新的珠宝定制订单', 'utf-8')
            message['From'] = sender
            message['To'] = self.receiver_email



            # 使用新的SMTP连接方式发送邮件
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender, password)
            server.send_message(message)
            server.quit()

            return True

        
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            messagebox.showerror("错误", f"发送邮件失败,请检查网络连接和邮箱配置")
            return False



    def create_widgets(self):
        # 主界面布局
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 素材库面板
        self.material_panel = ttk.LabelFrame(self.main_frame, text="素材库", width=200)
        self.material_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # 设计画布
        self.design_canvas = tk.Canvas(self.main_frame, bg="white", width=800, height=600)
        self.design_canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 加载背景图
        self.load_background()

        # 绑定事件
        self.design_canvas.bind("<Button-1>", self.place_material)
        self.design_canvas.bind("<B1-Motion>", self.drag_material)
        self.design_canvas.bind("<ButtonRelease-1>", self.release_material)


        # 创建一个控制按钮框架
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.TOP, pady=5)
    
        # 添加所有控制按钮
        self.start_button = ttk.Button(self.control_frame, text="开始设计", command=self.start_design)
        self.start_button.pack(side=tk.LEFT, padx=5)
    
        self.end_button = ttk.Button(self.control_frame, text="结束设计", command=self.end_design, state="disabled")
        self.end_button.pack(side=tk.LEFT, padx=5)
    
        self.undo_button = ttk.Button(self.control_frame, text="撤销", command=self.undo)
        self.undo_button.pack(side=tk.LEFT, padx=5)
    
        self.redo_button = ttk.Button(self.control_frame, text="重做", command=self.redo)
        self.redo_button.pack(side=tk.LEFT, padx=5)

        #在控制按钮框架中添加计算价格按钮
        self.calc_price_button = ttk.Button(self.control_frame, text="计算价格", command=self.calc_price)
        self.calc_price_button.pack(side=tk.LEFT, padx=5)
    

        # 更新按钮状态
        self.update_button_states()
    
    def calculate_total_price(self):
        """计算总价格并显示"""
        if not self.canvas_elements:
           messagebox.showinfo("价格计算", "请先设计珠宝")
           return
    
        total_price = 10   #基础价格
        for elem in self.canvas_elements:
            material_name = os.path.basename(elem["path"])
            if material_name in self.material_prices:   
                total_price += self.material_prices[material_name]
    
        # 显示价格并询问是否购买
        response = messagebox.askyesno(
            "价格计算", 
            f"设计总价格为: {total_price}元\n是否愿意购买？",
            icon='question'
        )
    
        if response:  # 如果愿意购买
            self.show_delivery_form()
        # 如果不愿意购买，对话框自动关闭

    def calc_price(self):
        """调用计算价格函数"""
        self.calculate_total_price()

       



    def start_design(self):
        """开始设计"""
        self.is_designing = True
        self.start_button["state"] = "disabled"
        self.end_button["state"] = "normal"
        
        # 启用所有设计相关控件
        self.design_canvas.bind("<Button-1>", self.place_material)
        self.design_canvas.bind("<B1-Motion>", self.drag_material)
        self.design_canvas.bind("<ButtonRelease-1>", self.release_material)
        
        # 启用素材选择
        for widget in self.material_panel.winfo_children():
            widget.bind("<Button-1>", lambda e, path=widget.image_path: self.select_material(path))
        
        # 启用撤销/重做按钮
        self.update_button_states()

        # 启用计算价格按钮
        self.calc_price_button["state"] = "normal"

    def end_design(self):
        """结束设计"""
        self.is_designing = False
        self.start_button["state"] = "normal"
        self.end_button["state"] = "disabled"

    
        # 禁用所有设计相关控件
        self.design_canvas.unbind("<Button-1>")
        self.design_canvas.unbind("<B1-Motion>")
        self.design_canvas.unbind("<ButtonRelease-1>")
    
        # 禁用素材选择
        for widget in self.material_panel.winfo_children():
            widget.unbind("<Button-1>")
    
        # 禁用撤销/重做按钮
        self.undo_button["state"] = "disabled"
        self.redo_button["state"] = "disabled"

        # 禁用计算价格按钮
        self.calc_price_button["state"] = "disabled"
    
        # 清除当前选中的素材
        self.selected_material = None

    
        # 清除画布上的所有元素
        for elem in self.canvas_elements:
            self.design_canvas.delete(elem["id"])
        self.canvas_elements.clear()
    
        # 清空历史记录
        self.history.clear()
        self.current_step = -1
    
        # 重新加载背景图
        self.load_background()

    def save_state(self):
        """保存当前状态到历史记录"""
        # 删除当前步骤之后的所有历史记录
        self.history = self.history[:self.current_step + 1]
        
        # 创建当前状态的快照
        current_state = [
            {
                "path": elem["path"],
                "x": elem["x"],
                "y": elem["y"]
            }
            for elem in self.canvas_elements
        ]
        
        # 添加到历史记录
        self.history.append(current_state)
        self.current_step += 1
        
        # 如果历史记录超过最大限制，删除最早的记录
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_step -= 1
            
        self.update_button_states()

    def update_button_states(self):
        """更新撤销/重做按钮状态"""
        self.undo_button["state"] = "normal" if self.current_step >= 0 else "disabled"
        self.redo_button["state"] = "normal" if self.current_step < len(self.history) - 1 else "disabled"

    def undo(self):
        """撤销操作"""
        if self.current_step >= 0:
            self.current_step -= 1
            self.restore_state()

    def redo(self):
        """重做操作"""
        if self.current_step < len(self.history) - 1:
            self.current_step += 1
            self.restore_state()

    def restore_state(self):
        """恢复到指定历史状态"""
        # 清除画布上的所有元素
        for elem in self.canvas_elements:
            self.design_canvas.delete(elem["id"])
        self.canvas_elements.clear()
        
        # 如果没有历史记录，直接返回
        if self.current_step < 0:
            self.update_button_states()
            return
            
        # 恢复历史状态
        state = self.history[self.current_step]
        for elem_data in state:
            try:
                img = Image.open(elem_data["path"])
                img = img.resize((30, 30), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                item = self.design_canvas.create_image(
                    elem_data["x"], 
                    elem_data["y"], 
                    image=photo
                )
                
                self.canvas_elements.append({
                    "id": item,
                    "image": photo,
                    "path": elem_data["path"],
                    "x": elem_data["x"],
                    "y": elem_data["y"]
                })
            except Exception as e:
                print(f"恢复状态失败: {e}")
                
        self.update_button_states()

    def load_background(self):
        try:
            self.bg_image = Image.open(self.background_image_path)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.design_canvas.create_image(0, 0, image=self.bg_photo, anchor=tk.NW)
        except Exception as e:
            print(f"无法加载背景图片: {e}")

    def load_materials(self):
        # 清空现有素材
        for widget in self.material_panel.winfo_children():
            widget.destroy()

        # 加载素材图片
        try:
            material_files = [f for f in os.listdir(self.material_folder) 
                            if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            for idx, filename in enumerate(material_files):
                img_path = os.path.join(self.material_folder, filename)
                img = Image.open(img_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                btn = ttk.Label(self.material_panel, image=photo)
                btn.image = photo  # 保持引用
                btn.image_path = img_path  # 保存图片路径
                btn.grid(row=idx//2, column=idx%2, padx=5, pady=5)

        except Exception as e:
            print(f"加载素材失败: {e}")

    def select_material(self, path):
        self.selected_material = path
        print(f"已选择素材: {os.path.basename(path)}")

    def place_material(self, event):
        if self.selected_material:
            try:
                img = Image.open(self.selected_material)
                img = img.resize((30, 30), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                item = self.design_canvas.create_image(event.x, event.y, image=photo)
                self.canvas_elements.append({
                    "id": item,
                    "image": photo,
                    "path": self.selected_material,
                    "x": event.x,
                    "y": event.y
                })
                self.dragging_item = item
            except Exception as e:
                print(f"放置素材失败: {e}")
        # 添加保存状态
        self.save_state()

    def drag_material(self, event):
        if self.dragging_item:
            self.design_canvas.coords(self.dragging_item, event.x, event.y)

    def release_material(self, event):
        if self.dragging_item:
            # 更新位置信息
            for elem in self.canvas_elements:
                if elem["id"] == self.dragging_item:
                    elem["x"] = event.x
                    elem["y"] = event.y
                    break
            self.dragging_item = None

            # 添加保存状态
            self.save_state()

    def save_design(self, filename):
        # 保存设计功能（需要扩展）
        design_data = {
            "background": self.background_image_path,
            "elements": [(elem["path"], elem["x"], elem["y"]) 
                       for elem in self.canvas_elements]
        }
        print(f"设计已保存: {design_data}")

if __name__ == "__main__":
    root = tk.Tk()
    app = JewelryDesigner(root)
    root.mainloop()