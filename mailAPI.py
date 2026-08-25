#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ELF2OS 商业使用授权协议 v1.0
====================================

版权所有 (C) 2026 anonymous123456988 (https://github.com/anonymous123456988)
保留所有权利 (All Rights Reserved)

本协议是 anonymous123456988（以下简称“授权方”）与您（以下简称“被授权方”）
之间关于 mailAPI.py 软件（以下简称“本软件”）的法律协议。

1. 授权范围
   授权方授予被授权方一份非独占、不可转让、不可再许可的永久使用权，
   允许被授权方：
   (1) 在单台计算机上安装并使用本软件；
   (2) 将本软件用于个人或企业内部项目；

2. 禁止行为
   被授权方不得：
   (1) 对本软件进行反向工程、反编译、反汇编或试图获取源代码；
   (2) 将本软件或其任何修改版本作为独立产品出售、出租、转让或再分发；
   (3) 将本软件嵌入其他商业产品中作为竞品功能；
   (4) 未经授权方书面同意，向任何第三方提供本软件的访问权限。

3. 知识产权
   本软件及其所有副本的知识产权（包括但不限于版权、商标权）均归授权方所有。
   本协议不授予被授权方任何所有权，仅授予使用权。

4. 免责声明
   本软件按“现状”提供，不提供任何明示或暗示的保证，
   包括但不限于适销性、特定用途适用性和非侵权性的保证。
   授权方不对因使用本软件造成的任何直接、间接、偶然、特殊或后果性损失承担责任。

5. 协议终止
   如被授权方违反本协议任何条款，本授权自动终止。
   协议终止后，被授权方必须立即停止使用本软件并销毁所有副本。

6. 其他
   本协议受中华人民共和国法律管辖。
   授权方保留随时修改本协议的权利，修改后的协议将发布于官方页面。

   如有任何疑问，请联系：https://github.com/anonymous123456988
"""

import smtplib
import json
import requests
import logging
import re
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from flask import Flask, request, jsonify
from flask_cors import CORS
import socket
import threading
from datetime import datetime

# ==================== 配置区域 ====================
EMAIL_CONFIG = {
    'smtp_server': 'smtp.qq.com',
    'smtp_port': 456,
    'sender_email': '3909296166@qq.com',
    'sender_password': 'nknkneyoetgxcfah',  # 改成你的授权码
}

SERVER_CONFIG = {
    'host': '0.0.0.0',
    'port': 8080,
    'debug': False
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ==================== 核心功能 ====================

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        if response.status_code == 200:
            return response.json().get('ip', 'unknown')
    except:
        pass
    return 'unknown'

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def send_email_qq(to_email, subject, content):
    """
    使用QQ邮箱发送邮件 - 多种方式尝试
    """
    # 方法1：使用465端口 + SSL（标准方式）
    try:
        if not validate_email(to_email):
            return False, f"邮箱格式无效: {to_email}"
        
        msg = MIMEMultipart()
        msg['From'] = Header(EMAIL_CONFIG['sender_email'])
        msg['To'] = Header(to_email)
        msg['Subject'] = Header(subject, 'utf-8')
        body = MIMEText(content, 'plain', 'utf-8')
        msg.attach(body)
        
        logger.info(f"尝试方式1: SSL连接 {EMAIL_CONFIG['smtp_server']}:465")
        
        # 创建SSL上下文，使用更宽松的设置
        context = ssl._create_unverified_context()
        
        server = smtplib.SMTP_SSL(
            EMAIL_CONFIG['smtp_server'],
            465,
            context=context,
            timeout=30
        )
        
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.sendmail(EMAIL_CONFIG['sender_email'], to_email, msg.as_string())
        server.quit()
        
        logger.info(f"✅ 邮件发送成功 (SSL): {to_email}")
        return True, "发送成功"
        
    except Exception as e:
        logger.warning(f"方式1失败: {str(e)}")
    
    # 方法2：使用587端口 + TLS
    try:
        if not validate_email(to_email):
            return False, f"邮箱格式无效: {to_email}"
        
        msg = MIMEMultipart()
        msg['From'] = Header(EMAIL_CONFIG['sender_email'])
        msg['To'] = Header(to_email)
        msg['Subject'] = Header(subject, 'utf-8')
        body = MIMEText(content, 'plain', 'utf-8')
        msg.attach(body)
        
        logger.info(f"尝试方式2: TLS连接 {EMAIL_CONFIG['smtp_server']}:587")
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], 587, timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.sendmail(EMAIL_CONFIG['sender_email'], to_email, msg.as_string())
        server.quit()
        
        logger.info(f"✅ 邮件发送成功 (TLS): {to_email}")
        return True, "发送成功"
        
    except Exception as e:
        logger.warning(f"方式2失败: {str(e)}")
    
    # 方法3：使用25端口（不加密）
    try:
        if not validate_email(to_email):
            return False, f"邮箱格式无效: {to_email}"
        
        msg = MIMEMultipart()
        msg['From'] = Header(EMAIL_CONFIG['sender_email'])
        msg['To'] = Header(to_email)
        msg['Subject'] = Header(subject, 'utf-8')
        body = MIMEText(content, 'plain', 'utf-8')
        msg.attach(body)
        
        logger.info(f"尝试方式3: 普通连接 {EMAIL_CONFIG['smtp_server']}:25")
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], 25, timeout=30)
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.sendmail(EMAIL_CONFIG['sender_email'], to_email, msg.as_string())
        server.quit()
        
        logger.info(f"✅ 邮件发送成功 (普通): {to_email}")
        return True, "发送成功"
        
    except Exception as e:
        logger.warning(f"方式3失败: {str(e)}")
    
    return False, "所有发送方式均失败，请检查网络和配置"

def send_callback_result(callback_url, to_email, success, content, message=""):
    """发送回调结果"""
    if not callback_url:
        return
    
    try:
        result_data = {
            'to_email': to_email,
            'success': success,
            'content': content,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"📤 发送回调到: {callback_url}")
        response = requests.post(
            callback_url,
            json=result_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ 回调成功")
        else:
            logger.warning(f"⚠️ 回调返回: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ 回调失败: {str(e)}")

# ==================== API路由 ====================

@app.route('/api/send_email', methods=['POST', 'GET'])
def api_send_email():
    """邮件发送API"""
    
    # GET请求（方便浏览器测试）
    if request.method == 'GET':
        to_email = request.args.get('to_email', '')
        content = request.args.get('content', '测试邮件')
        subject = request.args.get('subject', '验证码邮件')
        callback_url = request.args.get('callback_url', '')
        
        if not to_email:
            return jsonify({
                'to_email': '',
                'success': False,
                'content': '',
                'message': '缺少参数: to_email'
            }), 400
    
    # POST请求
    else:
        try:
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
                if not data:
                    raw = request.get_data(as_text=True)
                    data = json.loads(raw) if raw else {}
            
            to_email = data.get('to_email', '')
            content = data.get('content', '')
            subject = data.get('subject', '验证码邮件')
            callback_url = data.get('callback_url', '')
            
        except Exception as e:
            return jsonify({
                'to_email': '',
                'success': False,
                'content': '',
                'message': f'解析请求失败: {str(e)}'
            }), 400
    
    # 验证参数
    if not to_email:
        return jsonify({
            'to_email': '',
            'success': False,
            'content': content,
            'message': '缺少必填参数: to_email'
        }), 400
    
    if not content:
        return jsonify({
            'to_email': to_email,
            'success': False,
            'content': '',
            'message': '缺少必填参数: content'
        }), 400
    
    # 发送邮件
    success, message = send_email_qq(to_email, subject, content)
    
    # 构造返回
    response_data = {
        'to_email': to_email,
        'success': success,
        'content': content,
        'message': message
    }
    
    # 异步回调
    if callback_url:
        thread = threading.Thread(
            target=send_callback_result,
            args=(callback_url, to_email, success, content, message)
        )
        thread.daemon = True
        thread.start()
    
    status_code = 200 if success else 500
    return jsonify(response_data), status_code

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'server': 'Email API Service'
    })

@app.route('/api/info', methods=['GET'])
def api_info():
    return jsonify({
        'service': '邮箱验证码发送服务',
        'version': '1.0.0',
        'api_endpoints': {
            '/api/send_email': {
                'method': 'POST/GET',
                'parameters': {
                    'to_email': '目标邮箱（必填）',
                    'content': '邮件内容（必填）',
                    'subject': '邮件主题（可选）',
                    'callback_url': '回调地址（可选）'
                }
            }
        }
    })

# ==================== 主程序 ====================

def main():
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    port = SERVER_CONFIG['port']
    
    print("\n" + "="*60)
    print("📧 邮箱验证码发送服务 (修复版)")
    print("="*60)
    print(f"\n🚀 服务已启动！")
    print(f"\n📡 API访问地址：")
    print(f"   📍 内网地址: http://{local_ip}:{port}/api/send_email")
    print(f"   🌐 公网地址: http://{public_ip}:{port}/api/send_email")
    print("\n" + "="*60)
    print("📝 测试命令：")
    print(f"   curl \"http://localhost:{port}/api/send_email?to_email=test@qq.com&content=验证码1234\"")
    print("\n" + "="*60)
    print("⚠️  按 Ctrl+C 停止服务\n")
    
    try:
        app.run(
            host=SERVER_CONFIG['host'],
            port=SERVER_CONFIG['port'],
            debug=SERVER_CONFIG['debug'],
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("服务已停止")

if __name__ == '__main__':
    main()
