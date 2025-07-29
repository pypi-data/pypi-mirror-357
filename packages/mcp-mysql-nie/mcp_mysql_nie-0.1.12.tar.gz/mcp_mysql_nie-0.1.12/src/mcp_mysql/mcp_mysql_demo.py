from mcp.server.fastmcp import FastMCP
from mcp.server import Server
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from mysql.connector import connect, Error

mcp = FastMCP("MysqlService")
connections = {}

@mcp.tool()
def connect_db(host: str, port: int, user: str, password: str, database: str) -> str:
    """连接到 MySQL 数据库"""
    try:
        config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }
        if "conn" in connections:
            connections["conn"].close()
            del connections["conn"]
        connections["conn"] = connect(**config)
        return f"成功连接到数据库 {database} 在 {host}:{port} 作为用户 {user}"
    except Error as err:
        return f"连接数据库失败: {str(err)}"

@mcp.tool()
def execute_query(query: str) -> str:
    """执行 SQL 查询"""
    try:
        conn = connections.get("conn")
        if not conn:
            return f"未连接到数据库: {database}"
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return {"columns": columns, "rows": results}
    except Error as err:
        return f"执行语句 '{query}' 出错: {str(err)}"

@mcp.tool()
def list_tables() -> str:
    """列出当前数据库中的所有表"""
    try:
        conn = connections.get("conn")
        if not conn:
            return f"未连接到数据库: {database}"
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
    except Error as err:
        return f"获取表列表失败: {err}"

@mcp.tool()
def describe_table(table_name: str) -> str:
    """描述指定表的结构"""
    try:
        conn = connections.get("conn")
        if not conn:
            return f"未连接到数据库: {database}"
        with conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE {table_name}")
            description = cursor.fetchall()
            return [{"Field": row[0], "Type": row[1], "Null": row[2], "Key": row[3], "Default": row[4], "Extra": row[5]} for row in description]
    except Error as err:
        return f"获取表描述失败: {err}"

def main():
    """主函数，启动 MCP 服务器"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

    