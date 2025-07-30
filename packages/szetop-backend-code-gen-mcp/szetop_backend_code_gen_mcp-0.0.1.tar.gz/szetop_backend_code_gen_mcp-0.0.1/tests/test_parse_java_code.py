from backend_gen_server import ParseJavaEntity

java_entity_path = "d:\\projects\\ai\\ai-demo-api\\yitu-template\\src\\main\\java\\com\\yitu\\template\\api\\entity\\GxrcProjectInfo.java"

with open(java_entity_path, encoding="utf-8") as f:
    java_code = f.read()

parse = ParseJavaEntity(java_code)


def test_extract_table_info():
    """
    测试提取表信息
    """
    table_info = parse.extract_table_info()
    assert table_info.table_name == 'gxrc_project_info'
    assert table_info.description == '项目信息表'


def test_extract_table_fields():
    """
    测试提取表字段
    """
    fields = parse.extract_table_fields()
    for field in fields:
        if field.field_name == "projectCode":
            assert field.description == "房屋编码"
            assert field.db_field == "project_code"


def test_generate_ddl():
    """
    测试生成sql
    """
    table_info = ParseJavaEntity.extract_entity_info_by_path(java_entity_path)
    mysql_ddl = table_info.generate_mysql_ddl()
    assert len(mysql_ddl) > 100
    postgresql_ddl = table_info.generate_mysql_ddl()
    assert len(postgresql_ddl) > 100
    print(postgresql_ddl)


def test_all():
    test_extract_table_fields()
    test_extract_table_info()
