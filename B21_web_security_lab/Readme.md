# Web Application Security Lab

## Overview

In this lab, you will investigate and gain hands-on experience with common web application vulnerabilities. Specifically, you will explore techniques such as **SQL Injection** and **Stored Cross-Site Scripting (XSS)**. By the end of this lab, you should have a clearer understanding of how these attacks work and why secure coding practices are essential.

---

## Task 1: SQL Injection (Authentication Bypass)

In this task, your objective is to perform an **SQL injection attack** to bypass the login mechanism.

* Navigate to the login page located at: `/login_page`
* Analyze how user input is processed by the application
* Construct a malicious input that allows you to bypass authentication without valid credentials

**Goal:** Successfully log in without knowing a legitimate username and password.

---

## Task 2: Cross-Site Scripting (XSS)

After completing Task 1, you will proceed to exploit a **Cross-Site Scripting (XSS)** vulnerability.

* Your objective is to inject a payload that executes in the browser
* This task requires combining **HTML** and **JavaScript** to construct your payload
* The payload should be designed to retrieve or display sensitive information from the application

**Example Payload:**

```html
<img src=x onerror="fetch('/login_page').then(r=>r.text()).then(alert)">
```

* Study how this payload works
* Modify or extend it to achieve the task objectives

**Goal:** Demonstrate how XSS can be used to access or expose user-related data.

---

