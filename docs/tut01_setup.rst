Tutorial 1: Setup
=================

The examples make use of the well-known scott tiger schema.
In this step we will create, in Oracle, the scott schema and some objects.

.. note::

   It is assumed that you already have an Oracle and PostgreSQL accounts,
   with the appropriate privileges to create the scott user and objects.

*************
Oracle Schema
*************

Using your SQL tool of choice, use the following code to create the scott user and objects.

#. Create Scott

    With a privileged account create the scott user.
    The follwoing code creates the user, grants required privileges,
    sets the default tablespace, and alters the sessions current schema to scott,
    so that the tables can be created, and data inserted.
    Adjust as necessary.

    .. code-block:: sql

        CREATE USER scott IDENTIFIED BY tiger;
        GRANT CREATE SESSION, CREATE VIEW, RESOURCE, UNLIMITED TABLESPACE TO scott;
        ALTER USER scott DEFAULT TABLESPACE users;
        ALTER SESSION SET CURRENT_SCHEMA = scott;

    Now connect as the new scott user.

    .. note::

      To start the tutorial again, you'll need to drop the scott user on Oracle.

      .. code-block:: sql

          DROP USER SCOTT CASCADE;

#. Create the Tables

    The infamous dept and emp tables and an index.

    .. code-block:: sql

        CREATE TABLE dept
        ( deptno      NUMBER(2) CONSTRAINT pk_dept PRIMARY KEY,
          dname       VARCHAR2(14),
          loc         VARCHAR2(13)
        );

        COMMENT ON TABLE dept IS 'Department tutorial table';
        COMMENT ON COLUMN dept.dname IS 'Department name';

        CREATE TABLE emp
        ( empno       NUMBER(4) CONSTRAINT pk_emp PRIMARY KEY,
          ename       VARCHAR2(10),
          job         VARCHAR2(9),
          mgr         NUMBER(4),
          hiredate    DATE,
          sal         NUMBER(7,2),
          comm        NUMBER(7,2),
          deptno      NUMBER(2) CONSTRAINT fk_deptno REFERENCES dept
        );

        COMMENT ON TABLE emp IS 'Employee tutorial table';
        COMMENT ON COLUMN emp.sal IS 'Salary amount';

        CREATE INDEX emp_ename_idx ON emp(ename);


#. Insert the Data

    Let's insert the test data.

    .. code-block:: sql

        INSERT INTO dept VALUES (10,'ACCOUNTING','NEW YORK');
        INSERT INTO dept VALUES (20,'RESEARCH','DALLAS');
        INSERT INTO dept VALUES (30,'SALES','CHICAGO');
        INSERT INTO dept VALUES (40,'OPERATIONS','BOSTON');

        INSERT INTO emp VALUES (7369,'SMITH','CLERK',7902,to_date('17-12-1980','dd-mm-yyyy'),800,NULL,20);
        INSERT INTO emp VALUES (7499,'ALLEN','SALESMAN',7698,to_date('20-2-1981','dd-mm-yyyy'),1600,300,30);
        INSERT INTO emp VALUES (7521,'WARD','SALESMAN',7698,to_date('22-2-1981','dd-mm-yyyy'),1250,500,30);
        INSERT INTO emp VALUES (7566,'JONES','MANAGER',7839,to_date('2-4-1981','dd-mm-yyyy'),2975,NULL,20);
        INSERT INTO emp VALUES (7654,'MARTIN','SALESMAN',7698,to_date('28-9-1981','dd-mm-yyyy'),1250,1400,30);
        INSERT INTO emp VALUES (7698,'BLAKE','MANAGER',7839,to_date('1-5-1981','dd-mm-yyyy'),2850,NULL,30);
        INSERT INTO emp VALUES (7782,'CLARK','MANAGER',7839,to_date('9-6-1981','dd-mm-yyyy'),2450,NULL,10);
        INSERT INTO emp VALUES (7788,'SCOTT','ANALYST',7566,to_date('13-JUL-87','dd-mm-rr')-85,3000,NULL,20);
        INSERT INTO emp VALUES (7839,'KING','PRESIDENT',NULL,to_date('17-11-1981','dd-mm-yyyy'),5000,NULL,10);
        INSERT INTO emp VALUES (7844,'TURNER','SALESMAN',7698,to_date('8-9-1981','dd-mm-yyyy'),1500,0,30);
        INSERT INTO emp VALUES (7876,'ADAMS','CLERK',7788,to_date('13-JUL-87', 'dd-mm-rr')-51,1100,NULL,20);
        INSERT INTO emp VALUES (7900,'JAMES','CLERK',7698,to_date('3-12-1981','dd-mm-yyyy'),950,NULL,30);
        INSERT INTO emp VALUES (7902,'FORD','ANALYST',7566,to_date('3-12-1981','dd-mm-yyyy'),3000,NULL,20);
        INSERT INTO emp VALUES (7934,'MILLER','CLERK',7782,to_date('23-1-1982','dd-mm-yyyy'),1300,NULL,10);

#. And Finally

    .. code-block:: sql

        COMMIT;


The scott schema should now be ready.


****************
PostgreSQL Setup
****************

Using your SQL tool of choice, use the following code to create the required tutorial user and database,
ready for the migration steps.

#. Create the database.

    .. code-block:: sql

      create database easyo2p_db;

#. Create the user.

    .. code-block:: sql

      create user easyo2p_user with password 'easyo2p_pwd';
      grant create on database easyo2p_db to easyo2p_user;

PostgreSQL should now be ready for the next tutorial steps.
