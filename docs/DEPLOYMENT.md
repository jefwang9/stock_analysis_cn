# A股股票分析智能体 - 部署文档

## 🚀 部署指南

### 1. 环境要求

#### 系统要求
- **操作系统**: macOS 10.15+, Ubuntu 18.04+, Windows 10+
- **Python版本**: 3.9+
- **内存**: 最少4GB，推荐8GB+
- **存储**: 最少10GB可用空间
- **网络**: 稳定的互联网连接

#### 软件依赖
- Python 3.9+
- pip (Python包管理器)
- Git (版本控制)
- Redis (可选，用于缓存)

### 2. 安装步骤

#### 步骤1: 克隆项目
```bash
git clone <repository-url>
cd cn_stock_trading_agent
```

#### 步骤2: 创建虚拟环境
```bash
# 使用venv
python -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate
```

#### 步骤3: 安装依赖包
```bash
pip install -r requirements_core.txt
```

#### 步骤4: 配置环境变量
```bash
# 复制环境配置模板
cp env_example.txt .env

# 编辑配置文件
nano .env
```

#### 步骤5: 初始化数据库
```bash
python -c "from historical_data import HistoricalDataCollector; HistoricalDataCollector()"
```

### 3. 运行方式

#### 方式1: 基础功能测试
```bash
# 运行基础测试
python test_basic.py

# 运行单元测试
python test_units.py
```

#### 方式2: API服务器
```bash
# 启动API服务器
python api_server.py

# 访问API文档
# http://localhost:8000/docs
```

#### 方式3: Web界面
```bash
# 启动Web应用
python web_app.py

# 访问Web界面
# http://localhost:8080
```

#### 方式4: 主智能体
```bash
# 启动主智能体
python main_agent.py
```

### 4. Docker部署

#### 创建Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements_core.txt .
RUN pip install --no-cache-dir -r requirements_core.txt

COPY . .

# 创建必要目录
RUN mkdir -p data models logs temp

# 暴露端口
EXPOSE 8000 8080

# 启动命令
CMD ["python", "api_server.py"]
```

#### 构建和运行
```bash
# 构建镜像
docker build -t stock-trading-agent .

# 运行容器
docker run -d \
  --name stock-agent \
  -p 8000:8000 \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  stock-trading-agent
```

### 5. 生产环境部署

#### 使用Gunicorn部署API
```bash
# 安装Gunicorn
pip install gunicorn

# 启动API服务
gunicorn -w 4 -b 0.0.0.0:8000 api_server:app
```

#### 使用Nginx反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 使用systemd管理服务
```ini
# /etc/systemd/system/stock-agent.service
[Unit]
Description=A股股票分析智能体
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/cn_stock_trading_agent
Environment=PATH=/path/to/cn_stock_trading_agent/.venv/bin
ExecStart=/path/to/cn_stock_trading_agent/.venv/bin/python api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启用服务
sudo systemctl enable stock-agent
sudo systemctl start stock-agent
```

### 6. 监控和日志

#### 日志配置
```python
# 在config.py中配置日志
class LoggingConfig(BaseSettings):
    log_level: str = "INFO"
    log_file: str = "logs/trading_agent.log"
    max_log_size: str = "10MB"
    log_rotation: str = "1 day"
```

#### 监控脚本
```bash
#!/bin/bash
# monitor.sh

# 检查服务状态
if ! pgrep -f "api_server.py" > /dev/null; then
    echo "API服务未运行，正在重启..."
    cd /path/to/cn_stock_trading_agent
    source .venv/bin/activate
    nohup python api_server.py > logs/api.log 2>&1 &
fi

# 检查磁盘空间
DISK_USAGE=$(df /path/to/cn_stock_trading_agent | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "磁盘使用率过高: ${DISK_USAGE}%"
fi

# 检查内存使用
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.2f", $3*100/$2}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "内存使用率过高: ${MEMORY_USAGE}%"
fi
```

#### 定时任务
```bash
# 添加到crontab
# 每分钟检查服务状态
* * * * * /path/to/monitor.sh

# 每天凌晨2点清理日志
0 2 * * * find /path/to/cn_stock_trading_agent/logs -name "*.log" -mtime +7 -delete

# 每天收盘后15:30运行预测
30 15 * * 1-5 cd /path/to/cn_stock_trading_agent && source .venv/bin/activate && python -c "from main_agent import AStockTradingAgent; agent = AStockTradingAgent(); agent.predict_daily_sectors()"
```

### 7. 性能优化

#### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_stock_daily_code_date ON stock_daily(stock_code, trade_date);
CREATE INDEX idx_sector_daily_sector_date ON sector_daily(sector_name, trade_date);
CREATE INDEX idx_predictions_date ON predictions(date);
```

#### 缓存优化
```python
# 使用Redis缓存
import redis
from functools import wraps

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

#### 异步处理
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def async_data_collection():
    """异步数据收集"""
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [
            executor.submit(get_stock_data, code) 
            for code in stock_codes
        ]
        results = await asyncio.gather(*tasks)
    return results
```

### 8. 安全配置

#### API安全
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

# 添加认证
security = HTTPBearer()

@app.get("/api/protected")
async def protected_endpoint(token: str = Depends(security)):
    # 验证token
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Access granted"}
```

#### 数据加密
```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data).decode()
```

### 9. 备份和恢复

#### 数据备份
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/stock-agent"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
sqlite3 data/trading_agent.db ".backup $BACKUP_DIR/trading_agent_$DATE.db"

# 备份配置文件
cp config.py $BACKUP_DIR/config_$DATE.py
cp .env $BACKUP_DIR/env_$DATE

# 备份模型文件
tar -czf $BACKUP_DIR/models_$DATE.tar.gz models/

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.py" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

#### 数据恢复
```bash
#!/bin/bash
# restore.sh

BACKUP_DIR="/backup/stock-agent"
BACKUP_DATE=$1

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Available backups:"
    ls $BACKUP_DIR/*.db | sed 's/.*trading_agent_//' | sed 's/.db//'
    exit 1
fi

# 恢复数据库
cp $BACKUP_DIR/trading_agent_$BACKUP_DATE.db data/trading_agent.db

# 恢复模型文件
tar -xzf $BACKUP_DIR/models_$BACKUP_DATE.tar.gz

echo "恢复完成: $BACKUP_DATE"
```

### 10. 故障排除

#### 常见问题

**问题1: 模块导入失败**
```bash
# 解决方案
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pip install --upgrade pip
pip install -r requirements_core.txt
```

**问题2: 数据库连接失败**
```bash
# 检查数据库文件权限
ls -la data/trading_agent.db
chmod 664 data/trading_agent.db
```

**问题3: 网络连接问题**
```bash
# 检查网络连接
ping baidu.com
curl -I https://xueqiu.com
```

**问题4: 内存不足**
```bash
# 监控内存使用
free -h
ps aux --sort=-%mem | head -10
```

#### 日志分析
```bash
# 查看错误日志
tail -f logs/trading_agent.log | grep ERROR

# 分析API访问日志
grep "GET /api" logs/api.log | wc -l

# 查看性能日志
grep "slow" logs/trading_agent.log
```

### 11. 更新和维护

#### 更新流程
```bash
# 1. 备份当前版本
./backup.sh

# 2. 拉取最新代码
git pull origin main

# 3. 更新依赖
pip install -r requirements_core.txt

# 4. 运行测试
python test_units.py

# 5. 重启服务
sudo systemctl restart stock-agent
```

#### 维护任务
```bash
# 每日维护脚本
#!/bin/bash
# daily_maintenance.sh

# 清理临时文件
find temp/ -name "*.tmp" -mtime +1 -delete

# 压缩旧日志
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;

# 更新股票列表
python -c "from historical_data import HistoricalDataCollector; HistoricalDataCollector().get_stock_list()"

# 检查数据完整性
python -c "from historical_data import HistoricalDataCollector; print(HistoricalDataCollector().get_data_summary())"
```

### 12. 扩展和定制

#### 添加新的数据源
```python
class CustomDataCollector:
    def get_custom_data(self, symbol):
        # 实现自定义数据获取逻辑
        pass
```

#### 添加新的预测模型
```python
class CustomPredictionModel:
    def train(self, features, targets):
        # 实现自定义训练逻辑
        pass
    
    def predict(self, features):
        # 实现自定义预测逻辑
        pass
```

#### 添加新的可视化图表
```python
class CustomVisualizer:
    def create_custom_chart(self, data):
        # 实现自定义图表
        pass
```

## 📞 技术支持

如遇到部署问题，请检查：
1. Python版本和依赖包
2. 网络连接状态
3. 文件权限设置
4. 日志文件内容
5. 系统资源使用情况

## 🔄 版本更新

- **v1.0.0** - 初始版本，基础功能完整
- **v1.1.0** - 添加API接口和Web界面
- **v1.2.0** - 添加数据可视化功能
- **v1.3.0** - 性能优化和错误处理改进
