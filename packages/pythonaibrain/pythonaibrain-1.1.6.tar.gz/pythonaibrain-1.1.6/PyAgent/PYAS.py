from flask import Flask, request, jsonify
import json
import logging
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pyaitk import Brain

app = Flask(__name__)
host = '127.0.0.1'
port = 8080

class API:
    def __init__(self) -> bool:
        self.data = {}

@app.route('/')
def main():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PYAI</title>
      <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
    <style>
        *{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: black;
            color: #e7e7e7;
            min-height: 100vh;
            line-height: 1.5;
        }
        spline-viewer.robot-3d {
        position: fixed;
        top: 60px;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
      }

        .image-gradient{
            position: absolute;
            top: 0;
            right: 0;
            opacity: 0.5;
            z-index: -1;

        }

        .layer-blur{
            height: 0;
            width: 300rem;
            position: absolute;
            top: 20%;
            right: 0;
            box-shadow: 0 0 700px 15px white;
            rotate: -30deg;
            z-index: -1;
        }

        .container{
            width: 100%;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            overflow: hidden;
        }

        header{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 5rem;
            z-index: 999;
        }

        header h1{
            margin: 0;
            font-size: 3rem;
            font-weight: 300;
        }

        nav{
            display: flex;
            align-items: center;
            gap: 3rem;
            margin-left: -5%;
        }

        nav a{
            font-size: 1rem;
            letter-spacing: 0.1rem;
            transition: color 0.2s ease;
            text-decoration: none;
            color: inherit;
            cursor: pointer;
        }

        nav a:hover{
            color: #a7a7a7;
        }

        .btn-signing{
            background-color: #a7a7a7;
            color: black;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            border: none;
            font-size: 1rem;
            font-weight: 500;
            transition: background-color 0.2s ease;
            cursor: pointer;
        }

        .btn-signing:hover{
            background-color: white;
        }

        .highlight{
            font-weight: bolder;
        }

        main{
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: calc(90vh - 6rem);
        }

        .content{
            max-width: 40rem;
            margin-left: 10%;
            z-index: 999;
        }

        .tag-box{
            position: relative;
            width: 18rem;
            height: 2.5rem;
            border-radius: 50px;
            background: linear-gradient(to right, #656565, #7f42a7, #6608c5, #5300a0, #757575, #656565);
            background-size: 200%;
            animation: animationGradiant 2.5s linear infinite;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
        }

        @keyframes animationGradiant{
            to{
                background-position: 200%;
            }
        }

        .tag-box .tag{
            position: absolute;
            inset: 3px 3px 3px 3px;
            background-color: black;
            border-radius: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.5s ease;
            cursor: pointer;
        }

        .tag-box .tag:hover{
            color: #5300a0;
        }

        .content h1{
            font-size: 4rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            margin: 2rem 0;
            line-height: 1.2;
            text-shadow: 0 0 10px rgba(128, 128, 128, 0.418);
        }

        .description{
            font-size: 1.2rem;
            letter-spacing: 0.05em;
            max-width: 35rem;
            color: gray;
        }

        .buttons{
            display: flex;
            gap: 1rem;
            margin-top: 3rem;
        }

        .btn-get-started{
            text-decoration: none;
            border: 1px solid #2a2a2a;
            padding: 0.7rem 1.2rem;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            transition: background-color 0.2s ease;
        }

        .btn-get-started:hover{
            background-color: #1a1a1a;
        }

        .btn-signing-main{
            text-decoration: none;
            background-color: lightgray;
            color: black;
            padding: 0.6rem 2.5rem;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            transition: background-color 0.2s ease;
        }

        .btn-signing-main:hover{
            background-color: gray;
        }

        .robot-3d{
            position: absolute;
            top: 0;
            right: -20%;
        }

        @media (max-width: 1300px){
            header{
                padding: 1rem 0.5rem;
            }

            .content{
                margin-top: 85%;
            }

            .robot-3d{
                scale: 0.8;
                top: -20%;
                right: 2%;
            }
        }

        @media (max-width: 768px){
            header{
                padding: 1rem 0.1rem;
            }

            nav{
                display:none;
            }

            header h1{
                font-size: 2rem;
            }

            .btn-signing{
                padding: 0.6rem 1.5rem;
            }

            .content{
                margin-top: 25rem;
            }

            .robot-3d{
                scale: 0.5;
                top: -25%;
                right: 0;
            }

            .content{
                max-width: 30rem;
                margin-left: 10%;
            }

            .tag-box{
                width: 12rem;
            }

            .content h1{
                font-size: 2.5rem;
            }

            .description{
                font-size: 1rem;
            }

            .btn-get-started{
                font-size: 0.8rem;
                padding: 0.8rem 1.2rem;
            }

            .btn-signing-main{
                font-size: 0.8rem;
                padding: 0.8rem 2rem;
            }
        }
    </style>
</head>
<body>
    <div class='layer-blur'></div>
    <div class="container">
        <header data-aos="fade-down">
            <h1 class="logo" data-aos="fade-down">PYAI</h1>

            <nav>
                <a href="/company" data-aos="fade-down">COMPANY</a>
                <a href="#" data-aos="fade-down">FEATURES</a>
                <a href="#" data-aos="fade-down">RESOUECES</a>
                <a href="/document" data-aos="fade-down">DOC</a>
                <a href="/doc" data-aos="fade-down">PYTHON DOC</a>
            </nav>
            <form action='/DashBoard' methods='post'>
                <button class="btn-signing" data-aos="fade-down" type='submit' href='DashBoard'>Getstarted &gt;</button>
            </form>
        </header>


        <spline-viewer class="robot-3d" url="https://prod.spline.design/959ny6S9DA3mLaif/scene.splinecode"></spline-viewer>
    </div>
    <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
    <script>
      AOS.init();
    </script>
    <img src="#" alt="">
    <script type="module" src="https://unpkg.com/@splinetool/viewer@1.9.82/build/spline-viewer.js"></script>
    <!--<spline-viewer url="https://prod.spline.design/A7kM-EXRqh14Wo-q/scene.splinecode"></spline-viewer>-->
</body>
</html>'''

@app.route('/DashBoard')
def dbs():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DashBoard</title>
      <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
    <style>
        *{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: black;
            color: #e7e7e7;
            min-height: 100vh;
            line-height: 1.5;
        }

        .image-gradient{
            position: absolute;
            top: 0;
            right: 0;
            opacity: 0.5;
            z-index: -1;

        }

        .layer-blur{
            height: 0;
            width: 300rem;
            position: absolute;
            top: 20%;
            right: 0;
            box-shadow: 0 0 700px 15px white;
            rotate: -30deg;
            z-index: -1;
        }

        .container{
            width: 100%;
            margin: 0 auto;
            padding: 0 2rem;
            position: relative;
            overflow: hidden;
        }

        header{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 5rem;
            z-index: 999;
        }

        header h1{
            margin: 0;
            font-size: 3rem;
            font-weight: 300;
        }

        nav{
            display: flex;
            align-items: center;
            gap: 3rem;
            margin-left: -5%;
        }

        nav a{
            font-size: 1rem;
            letter-spacing: 0.1rem;
            transition: color 0.2s ease;
            text-decoration: none;
            color: inherit;
            cursor: pointer;
        }

        nav a:hover{
            color: #a7a7a7;
        }

        spline-viewer{
            display: fixed;
        }

        .btn-signing{
            background-color: #a7a7a7;
            color: black;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            border: none;
            font-size: 1rem;
            font-weight: 500;
            transition: background-color 0.2s ease;
            cursor: pointer;
        }

        .btn-signing:hover{
            background-color: white;
        }

        .highlight{
            font-weight: bolder;
        }

        main{
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: calc(90vh - 6rem);
        }

        .content{
            max-width: 40rem;
            margin-left: 10%;
            z-index: 999;
        }

        .tag-box{
            position: relative;
            width: 18rem;
            height: 2.5rem;
            border-radius: 50px;
            background: linear-gradient(to right, #656565, #7f42a7, #6608c5, #5300a0, #757575, #656565);
            background-size: 200%;
            animation: animationGradiant 2.5s linear infinite;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
        }

        @keyframes animationGradiant{
            to{
                background-position: 200%;
            }
        }

        .tag-box .tag{
            position: absolute;
            inset: 3px 3px 3px 3px;
            background-color: black;
            border-radius: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.5s ease;
            cursor: pointer;
        }

        .tag-box .tag:hover{
            color: #5300a0;
        }

        .content h1{
            font-size: 4rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            margin: 2rem 0;
            line-height: 1.2;
            text-shadow: 0 0 10px rgba(128, 128, 128, 0.418);
        }

        .description{
            font-size: 1.2rem;
            letter-spacing: 0.05em;
            max-width: 35rem;
            color: gray;
        }

        .buttons{
            display: flex;
            gap: 1rem;
            margin-top: 3rem;
        }

        .btn-get-started{
            text-decoration: none;
            border: 1px solid #2a2a2a;
            padding: 0.7rem 1.2rem;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            transition: background-color 0.2s ease;
        }

        .btn-get-started:hover{
            background-color: #1a1a1a;
        }

        .btn-signing-main{
            text-decoration: none;
            background-color: lightgray;
            color: black;
            padding: 0.6rem 2.5rem;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            transition: background-color 0.2s ease;
        }

        .btn-signing-main:hover{
            background-color: gray;
        }

        .robot-3d{
            position: fixed;
            top: 0;
            right: -20%;
            display: fixed;
            z-index: -1;
        }

        @media (max-width: 1300px){
            header{
                padding: 1rem 0.5rem;
            }

            .content{
                margin-top: 85%;
            }

            .robot-3d{
                scale: 0.8;
                top: -20%;
                right: 2%;
            }
        }

        @media (max-width: 768px){
            header{
                padding: 1rem 0.1rem;
            }

            nav{
                display:none;
            }

            header h1{
                font-size: 2rem;
            }

            .btn-signing{
                padding: 0.6rem 1.5rem;
            }

            .content{
                margin-top: 25rem;
            }

            .robot-3d{
                scale: 0.5;
                top: -25%;
                right: 0;
            }

            .content{
                max-width: 30rem;
                margin-left: 10%;
            }

            .tag-box{
                width: 12rem;
            }

            .content h1{
                font-size: 2.5rem;
            }

            .description{
                font-size: 1rem;
            }

            .btn-get-started{
                font-size: 0.8rem;
                padding: 0.8rem 1.2rem;
            }

            .btn-signing-main{
                font-size: 0.8rem;
                padding: 0.8rem 2rem;
            }
        }
    </style>
</head>
<body>
    <div class='layer-blur'></div>
    <div class="container">
        <header data-aos="fade-down">
            <h1 class="logo" data-aos="fade-down">PYAI</h1>

            <nav>
                <a href="#" data-aos="fade-down">COMPANY</a>
                <a href="#" data-aos="fade-down">FEATURES</a>
                <a href="#" data-aos="fade-down">Get API</a>
                <a href="/document" data-aos="fade-down">DOC</a>
                <a href="/doc" data-aos="fade-down">Python DOC</a>
            </nav>

            <button class="btn-signing" data-aos="fade-down">SIGNING</button>
        </header>

        <main>
            <div class="content">
                <div class="tag-box" data-aos="fade-right">
                    <div class="tag" href='/doc'>INTRODUCTION &wedbar; </div>
                </div>

                <h1 data-aos="fade-right">PYAI FOR<br data-aos="fade-right">DEVELOPERS</h1>

                <p class="description" data-aos="fade-right">
                    Use PYAI to for making your own AI Assistance. <br>
                    <span class="highlight">PYAI</span> is a new way to reach your team and get things done. <br>
                </p>

                <div class="buttons">
                    <a href="/doc" class="btn-get-started" data-aos="fade-right">Documentation &gt;</a>
                    <a href="/chat" class="btn-signing-main" data-aos="fade-right">Getstarted &gt;</a>

                </div>

            </div>
        </main>
        <spline-viewer class="robot-3d" url="https://prod.spline.design/A7kM-EXRqh14Wo-q/scene.splinecode"></spline-viewer>
    </div>
    <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
    <script>
      AOS.init();
    </script>
    <img src="#" alt="">
    <script type="module" src="https://unpkg.com/@splinetool/viewer@1.9.82/build/spline-viewer.js"></script>
    <!--<spline-viewer url="https://prod.spline.design/A7kM-EXRqh14Wo-q/scene.splinecode"></spline-viewer>-->
</body>
</html>'''

@app.route('/chat')
def chat():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PYAI Chat</title>
      <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
      <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        *{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: black;
            color: #e7e7e7;
            min-height: 100vh;
            line-height: 1.5;
            font-size: 20px;
        }

        .image-gradient{
            position: absolute;
            top: 0;
            right: 0;
            opacity: 0.5;
            z-index: -1;

        }

        .layer-blur{
            height: 0;
            width: 300rem;
            position: absolute;
            top: 20%;
            right: 0;
            box-shadow: 0 0 700px 15px white;
            rotate: -30deg;
            z-index: -1;
        }

        .container{
            width: 100%;
            margin: 0 auto;
            padding: 0 2rem;
            position: fixed;
            overflow-x: visible;
            overflow-y: hidden;
        }

        header{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 5rem;
            z-index: 999;
        }

        header h1{
            margin: 0;
            font-size: 3rem;
            font-weight: 300;
        }

        nav{
            display: flex;
            align-items: center;
            gap: 3rem;
            margin-left: -5%;
        }

        nav a{
            font-size: 1rem;
            letter-spacing: 0.1rem;
            transition: color 0.2s ease;
            text-decoration: none;
            color: inherit;
            cursor: pointer;
        }

        nav a:hover{
            color: #a7a7a7;
        }

        .chat-container {
            position: fixed;
            scrollbar-width: thin;
            scrollbar-color: #444 #1a1a1a;
            top: 20%;
            bottom: 10%;
            left: 10%;
            width: 80%;
            overflow-y: auto;
            overflow-x: hidden;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            overflow-x: hidden;  /* No horizontal scroll for container */
            overflow-y: auto;
            max-width: 100vw;
        }

        .send-btn {
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
        }

        .send-icon {
          width: 24px;
          height: 24px;
          fill: white;
        }

        .message {
            background-color: rgba(255,255,255,0.1);
            padding: 1rem;
            border-radius: 8px;
            max-width: 75%;
            overflow-wrap: break-word; /* ✅ modern replacement for word-wrap */
            word-break: break-word;     /* ✅ breaks long words */
            white-space: pre-wrap;
            max-width: 100%;  /* Make sure message containers don’t exceed their parent */
            word-wrap: break-word; /* Break long words */
            overflow-wrap: break-word;
        }

        .message.user {
            align-self: flex-end;
            background-color: rgba(0,255,0,0.1);
        }

        .message.bot {
            align-self: flex-start;
            background-color: rgba(0,0,255,0.1);
        }

        /* Code blocks */
        .message pre {
            background-color: #1e1e1e;
            color: #eaeaea;
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Courier New', Courier, monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        /* Inline code */
        .message code {
            background-color: #2a2a2a;
            color: #ffd369;
            padding: 0.2em 0.4em;
            border-radius: 4px;
            font-size: 0.95em;
            font-family: 'Courier New', Courier, monospace;
        }

        /* Headings */
        .message h1, .message h2, .message h3 {
            color: #ffcc00;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        /* Lists */
        .message ul {
            margin-left: 1.5rem;
            list-style-type: disc;
        }

        /* Links */
        .message a {
            color: #4fc3f7;
            text-decoration: underline;
        }


        /* Tables */
        .message table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            margin-bottom: 1rem;
            background-color: #1e1e1e;
            color: #eaeaea;
            border-radius: 6px;
            overflow: hidden;
            font-size: 0.95rem;
            width: 100%;      /* Table fits inside message */
            table-layout: fixed; /* Fix layout to avoid expanding */
            word-break: break-word; /* Wrap long content inside cells */
            overflow-x: auto; /* Allow horizontal scroll if needed */
            display: block;   /* Needed for overflow-x to work */
        }

        /* Table headers */
        .message th {
            background-color: #333;
            color: #ffd369;
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid #444;
        }

        /* Table cells */
        .message td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #444;
        }

        /* Responsive overflow */
        .message table {
            display: block;
            overflow-x: auto;
        }


        spline-viewer.robot-3d {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          z-index: -1;
        }

        .btn-signing{
            background-color: #a7a7a7;
            color: black;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            border: none;
            font-size: 1rem;
            font-weight: 500;
            transition: background-color 0.2s ease;
            cursor: pointer;
        }

        .btn-signing:hover{
            background-color: white;
        }

        .highlight{
            font-weight: bolder;
        }

        main{
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: calc(90vh - 6rem);
        }

        .content{
            max-width: 40rem;
            margin-left: 10%;
            z-index: 999;
        }

        .tag-box{
            position: relative;
            width: 18rem;
            height: 2.5rem;
            border-radius: 50px;
            background: linear-gradient(to right, #656565, #7f42a7, #6608c5, #5300a0, #757575, #656565);
            background-size: 200%;
            animation: animationGradiant 2.5s linear infinite;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
        }

        @keyframes animationGradiant{
            to{
                background-position: 200%;
            }
        }

        .tag-box .tag{
            position: absolute;
            inset: 3px 3px 3px 3px;
            background-color: black;
            border-radius: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: 0.5s ease;
            cursor: pointer;
        }

        .tag-box .tag:hover{
            color: #5300a0;
        }

        .content h1{
            font-size: 4rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            margin: 2rem 0;
            line-height: 1.2;
            text-shadow: 0 0 10px rgba(128, 128, 128, 0.418);
        }

        .glass {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-radius: 10px;
          padding: 1rem;
        }

        .txt-box{
          buttom : 5%;
          color: white;
          width: 95%;
          outline : none;
          display: fixed;
        }

        .description{
            font-size: 1.2rem;
            letter-spacing: 0.05em;
            max-width: 35rem;
            color: gray;
        }

        .buttons{
            display: flex;
            gap: 1rem;
            margin-top: 3rem;
        }

        .btn-get-started{
            text-decoration: none;
            border: 1px solid #2a2a2a;
            padding: 0.7rem 1.2rem;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            transition: background-color 0.2s ease;
        }

        .btn-get-started:hover{
            background-color: #1a1a1a;
        }

        .btn-signing-main{
            text-decoration: none;
            background-color: lightgray;
            color: black;
            padding: 0.6rem 2.5rem;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            transition: background-color 0.2s ease;
        }

        .btn-signing-main:hover{
            background-color: gray;
        }

        .robot-3d{
            position: absolute;
            top: 0;
            right: 0%;
            display: fixed;
        }

        @media (max-width: 1300px){
            header{
                padding: 1rem 0.5rem;
            }

            .content{
                margin-top: 85%;
            }

            .robot-3d{
                scale: 0.8;
                top: -20%;
                right: 2%;
            }
        }

        @media (max-width: 768px){
            header{
                padding: 1rem 0.1rem;
            }

            nav{
                display:none;
            }

            header h1{
                font-size: 2rem;
            }

            .btn-signing{
                padding: 0.6rem 1.5rem;
            }

            .content{
                margin-top: 25rem;
            }

            .robot-3d{
                scale: 0.5;
                top: -25%;
                right: 0;
            }

            .content{
                max-width: 30rem;
                margin-left: 10%;
            }

            .tag-box{
                width: 12rem;
            }

            .content h1{
                font-size: 2.5rem;
            }

            .description{
                font-size: 1rem;
            }

            .btn-get-started{
                font-size: 0.8rem;
                padding: 0.8rem 1.2rem;
            }

            .btn-signing-main{
                font-size: 0.8rem;
                padding: 0.8rem 2rem;
            }
        }
    </style>
</head>
<body>
    <div class='layer-blur'></div>
    <div class="container">
        <header data-aos="fade-down">
            <h1 class="logo" data-aos="fade-down">PYAI</h1>

            <!--<nav>
                <a href="#" data-aos="fade-down">COMPANY</a>
                <a href="#" data-aos="fade-down">FEATURES</a>
                <a href="#" data-aos="fade-down">RESOUECES</a>
                <a href="/doc" data-aos="fade-down">DOC</a>
            </nav>-->
            <form action='/DashBoard' methods='post'>
                <button class="btn-signing" data-aos="fade-down" type='submit' href='DashBoard'>Go Back &gt;</button>
            </form>
        </header>
        
        <main>
            <spline-viewer class="robot-3d" url="https://prod.spline.design/7T5L5TgvwxwAznRi/scene.splinecode"></spline-viewer>
            <br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>
            <form action='/PyAI' methods='post'>
                <div class="chat-container" id="chat-container">I'm Python AI how can I assist you today?
                  <!-- Messages will go here -->
                </div>
                <br>
                <textarea type='text' id="userInput" placeholder='Ask Anything' class="glass txt-box"></textarea>
                <button onclick="sendMessage()" class="glass" style="padding: 0.75rem 1.2rem; background-color: #444; color: white; border: none; border-radius: 6px; cursor: pointer;">Send<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="white" viewBox="0 0 24 24" style="display: flex;" class="send-icon">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg></button>
            </form>
        </main>
    
    </div>
    <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
    <script>
      const inputBox = document.getElementById("userInput");
        const chatContainer = document.getElementById("chat-container");

        inputBox.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                const userMessage = inputBox.value.trim();
                if (userMessage !== "") {
                    addMessage(userMessage, "user");
                    inputBox.value = "";

                    fetch("/PyAI", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ message: userMessage })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.response) {
                            addMessage(data.response, "bot");
                        }
                    });
                }
            }
        });

        function addMessage(message, sender) {
            const msg = document.createElement("div");
            msg.className = `message ${sender}`;
            msg.innerHTML = marked.parse(message);
            chatContainer.appendChild(msg);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
      AOS.init();
    </script>
    <img src="#" alt="">
    <script type="module" src="https://unpkg.com/@splinetool/viewer@1.9.82/build/spline-viewer.js"></script>
    <!--<spline-viewer url="https://prod.spline.design/A7kM-EXRqh14Wo-q/scene.splinecode"></spline-viewer>-->
</body>
</html>
'''

@app.route('/bot')
def bot():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python AI</title>
    <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: black;
            color: #e7e7e7;
            min-height: 100vh;
            line-height: 1.5;
        }

        .container {
            background-size: cover; /* Adjusted from 200% */
            background-attachment: fixed; /* Corrected from background-position */
            background-color: black;
            /* Removed border-color as it's not effective without border-width and border-style */
        }
    </style>
</head>
<body>
    <div class="container">
        <iframe src="https://nextjs-ai-chatbot-flame-eight-56.vercel.app/chat/034a89cf-36fa-4595-8df0-71bb214e81b7" width="1340px" height="640px"></iframe>
    </div>
</body>
</html>'''

@app.route('/chats')
def data():
    return 'https://nextjs-ai-chatbot-flame-eight-56.vercel.app/chat/034a89cf-36fa-4595-8df0-71bb214e81b7'

@app.route('/doc')
def doc():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About Python</title>
    <style>
        :root {
            --bg-color: #f4f4f9;
            --text-color: #333;
            --header-bg: #306998;
            --highlight-bg: #e0f7fa;
            --highlight-border: #00796b;
            --footer-bg: #ddd;
            --button-bg: #306998;
            --button-hover: #28527a;
            --code-bg: #eee;
            --pre-bg: #f0f0f0;
            --keyword-color: orange;
            --class-color: green;
            --function-color: blue;
            --comment-color: darkgreen;
            --singleLine-color: red;
        }

        [data-theme="dark"] {
            --bg-color: #121212;
            --text-color: #e0e0e0;
            --header-bg: #1e3a5f;
            --highlight-bg: #2c3e50;
            --highlight-border: #16a085;
            --footer-bg: #1c1c1c;
            --button-bg: #1e3a5f;
            --button-hover: #16324b;
            --code-bg: #2c2c2c;
            --pre-bg: #1e1e1e;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
        }
        header {
            background-color: var(--header-bg);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 2rem;
        }
        nav {
            background-color: var(--footer-bg);
            padding: 10px;
            text-align: center;
        }
        nav a {
            margin: 0 15px;
            text-decoration: none;
            color: var(--text-color);
            font-weight: bold;
        }
        main {
            padding: 40px;
            max-width: 900px;
            margin: auto;
            line-height: 1.8;
        }
        h2 {
            color: var(--header-bg);
        }
        .highlight {
            background-color: var(--highlight-bg);
            padding: 10px;
            border-left: 4px solid var(--highlight-border);
            margin: 20px 0;
        }
        footer {
            background-color: var(--footer-bg);
            text-align: center;
            padding: 15px;
            margin-top: 40px;
        }
        button {
            background-color: var(--button-bg);
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-size: 1rem;
            border-radius: 5px;
            margin-top: 15px;
        }
        button:hover {
            background-color: var(--button-hover);
        }
        code {
            background-color: var(--code-bg);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
        pre {
            background-color: var(--pre-bg);
            padding: 15px;
            border-left: 4px solid #ccc;
            overflow-x: auto;
        }
        .dark-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }

        .import{
            color: var(--keyword-color);
        }

        .function{
            color: var(--function-color);
        }

        .class{
            color: var(--class-color);
        }

        .comment{
            color: var(--comment-color);
        }

        .single{
            color: var(--singleLine-color);
        }
    </style>
</head>
<body>
    <button class="dark-toggle" onclick="toggleDarkMode()">Toggle Dark Mode</button>
    <header>
        About Python
    </header>
    <nav>
        <a href="#intro">What is Python?</a>
        <a href="#keywords">Keywords</a>
        <a href="#modules">Modules</a>
        <a href="#symbols">Symbols</a>
        <a href="#topics">Topics</a>
        <a href="#example">Example</a>
        <a href="#howtodoc">Python Docs</a>
    </nav>
    <main>
        <h2 id="intro">What is Python?</h2>
        <p>Python is a high-level, interpreted programming language known for its simplicity and readability. Created by <strong>Guido van Rossum</strong> and first released in 1991, Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming. It is widely used in web development, data science, AI, automation, and more.</p>

        <h2 id="keywords">Python Keywords</h2>
        <p>Keywords are reserved words that cannot be used as identifiers. Some commonly used keywords include:</p>
        <ul>
            <li><code>if</code>, <code>else</code>, <code>elif</code> – Conditional branching</li>
            <li><code>for</code>, <code>while</code>, <code>break</code>, <code>continue</code> – Loop control</li>
            <li><code>def</code>, <code>return</code>, <code>lambda</code> – Functions</li>
            <li><code>import</code>, <code>from</code>, <code>as</code> – Module handling</li>
            <li><code>try</code>, <code>except</code>, <code>finally</code> – Exception handling</li>
            <li><code>class</code>, <code>self</code>, <code>init</code> – Object-oriented programming</li>
        </ul>

        <h2 id="modules">Built-in Modules</h2>
        <p>Python has a large standard library with built-in modules such as:</p>
        <ul>
            <li><code>math</code> – Mathematical functions</li>
            <li><code>random</code> – Random number generation</li>
            <li><code>datetime</code> – Date and time manipulation</li>
            <li><code>os</code> – Operating system interactions</li>
            <li><code>sys</code> – System-specific parameters and functions</li>
            <li><code>json</code> – JSON parsing and formatting</li>
        </ul>

        <h2 id="symbols">Python Symbols</h2>
        <p>Python uses various symbols as part of its syntax:</p>
        <ul>
            <li><code>=</code> – Assignment</li>
            <li><code>==</code>, <code>!=</code>, <code>&lt;</code>, <code>&gt;</code> – Comparison</li>
            <li><code>#</code> – Single-line comment</li>
            <li><code>*</code>, <code>**</code> – Multiplication and exponentiation</li>
            <li><code>[]</code> – Lists, indexing</li>
            <li><code>{}</code> – Dictionaries, sets</li>
            <li><code>:</code> – Start of a block</li>
        </ul>

        <h2 id="topics">Important Python Topics</h2>
        <ul>
            <li>Variables and Data Types</li>
            <li>Operators</li>
            <li>Control Structures (if, elif, else)</li>
            <li>Loops (for, while)</li>
            <li>Functions</li>
            <li>Modules and Packages</li>
            <li>File Handling</li>
            <li>Object-Oriented Programming</li>
            <li>Error Handling</li>
            <li>Decorators & Generators</li>
            <li>List Comprehensions</li>
            <li>Regular Expressions</li>
        </ul>

        <h2 id="example">Basic Python Program Example</h2>
        <p>Here’s a simple Python program that adds two numbers entered by the user:</p>
        <pre><code><span class='single'># This program adds two numbers provided by the user</span>

num1 = <span class='function'>input</span>(<span class='comment'>"Enter first number: "</span>)
num2 = <span class='function'>input</span>(<span class='comment'>"Enter second number: "</span>)

<span class='single'># Adding the two numbers (after converting to float)</span>
sum = <span class='class'>float</span>(num1) + <span class='class'>float</span>(num2)

<span class='single'># Display the sum</span>
<span class='function'>print</span>(<span class='comment'>"The sum is:"</span>, sum)</code></pre>

        <h2 id="howtodoc">How to Write Python Documentation</h2>
        <p>You can document your Python code using comments, docstrings, and documentation generators like Sphinx. Here's a simple docstring example:</p>
        <pre><code><span class='import'>def</span> <span class='function'>greet</span>(name):
    <span class='comment'>"""Returns a greeting for the given name."""</span>
    <span class='import'>return</span> f<span class='comment'>"Hello, </span>{name}<span class='comment'>!"</span>

<span class='function'>print</span>(<span class='function'>greet</span>(<span class='comment'>"Alice"</span>))</code></pre>
        <p>To create full documentation, you can:</p>
        <ul>
            <li>Use triple-quoted strings (<code>"""</code>) below functions and classes.</li>
            <li>Install <code>sphinx</code> using <code>pip install sphinx</code>.</li>
            <li>Run <code>sphinx-quickstart</code> and follow the prompts.</li>
            <li>Write `.rst` files for your modules and build HTML docs using <code>make html</code>.</li>
        </ul>

        <button onclick="showFact()">Click to See a Fun Fact About Python</button>
        <p id="fact" style="margin-top: 20px; font-weight: bold;"></p>
    </main>
    <footer>
        &copy; 2025 | Python Info Document | Created by Divyanshu | Hosted on <a href="https://codephantom-labs.com" target="_blank">CodePhantom Labs</a>
    </footer>

    <script>
        function showFact() {
            const facts = [
                "The name 'Python' comes from the British comedy group Monty Python.",
                "Python 2 was officially discontinued in 2020.",
                "Python is one of the most taught languages in universities worldwide.",
                "Python's creator, Guido van Rossum, was known as the 'Benevolent Dictator For Life' of Python."
            ];
            const randomIndex = Math.floor(Math.random() * facts.length);
            document.getElementById('fact').innerText = facts[randomIndex];
        }

        function toggleDarkMode() {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            if (currentTheme === "dark") {
                document.documentElement.removeAttribute("data-theme");
            } else {
                document.documentElement.setAttribute("data-theme", "dark");
            }
        }
    </script>
</body>
</html>
'''
# API

@app.route('/document')
def pyaiDocument():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link rel="icon" href="favicon.jpg" type="image/jpeg" />
  <title>PythonAI Brain Documentation</title>
  <style>
    /* Global GitHub Dark Theme */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-color: #0d1117;
      color: #c9d1d9;
      line-height: 1.6;
      padding: 20px;
    }

    header {
      background-color: #161b22;
      color: #c9d1d9;
      padding: 30px 20px;
      text-align: center;
      border: 1px solid #30363d;
      border-radius: 10px;
      margin-bottom: 20px;
      box-shadow: 0 0 10px rgba(0,0,0,0.4);
    }

    nav ul {
      list-style: none;
      background-color: #161b22;
      display: flex;
      justify-content: center;
      gap: 20px;
      padding: 15px;
      border: 1px solid #30363d;
      border-radius: 10px;
      margin-bottom: 20px;
    }

    nav ul li a {
      color: #58a6ff;
      text-decoration: none;
      font-weight: 600;
      transition: color 0.3s ease;
    }

    nav ul li a:hover {
      color: #79c0ff;
    }

    main {
      background-color: #161b22;
      padding: 25px;
      border: 1px solid #30363d;
      border-radius: 10px;
      box-shadow: 0 0 5px rgba(0,0,0,0.2);
    }

    h2, h3, h4, h5 {
      color: #58a6ff;
      margin-bottom: 10px;
    }

    section, article {
      margin-bottom: 30px;
    }

    /* Code Block Styling */
    pre {
      background-color: #1e1e1e;
      padding: 15px;
      border-left: 5px solid #58a6ff;
      overflow-x: auto;
      border-radius: 6px;
      font-size: 0.95rem;
    }

    code {
      font-family: 'Fira Code', 'Courier New', monospace;
      color: #dcdcdc;
    }

    /* Syntax Highlighting */
    .code-keyword { color: #ff7b72; font-weight: bold; }    /* def, return, if */
    .code-func    { color: #d2a8ff; }                        /* functions */
    .code-str     { color: #a5d6ff; }                        /* strings */
    .code-num     { color: #f2cc60; }                        /* numbers */
    .code-comment { color: #8b949e; font-style: italic; }   /* comments */
    .code-operator { color: #79c0ff; }                      /* operators */
    .code-attr    { color: #c9d1d9; }                        /* attributes */
    .code-class   { color: #09a5b9; font-weight: bold; }    /* class names */

    ul {
      padding-left: 20px;
    }

    a {
      color: #58a6ff;
    }

    a:hover {
      color: #79c0ff;
    }

    footer {
      text-align: center;
      padding: 20px;
      background-color: #161b22;
      border: 1px solid #30363d;
      color: #8b949e;
      border-radius: 10px;
      margin-top: 30px;
    }
  </style>
</head>
<body>
  <header>
    <h1>PythonAI Brain</h1>
    <p>Make your first AI Assistant in Python. No complex setup, no advanced coding. Just install, configure, and run!</p>
  </header>

  <nav>
    <ul>
      <li><a href="#installation">Installation</a></li>
      <li><a href="#modules">Modules</a></li>
      <li><a href="#pybrain">PyBrain Assistant</a></li>
    </ul>
  </nav>

  <main>
    <h2 id="example">Example Python Code</h2>
    <pre><code>
<span class="code-comment"># Example of simple PythonAI function</span>
<span class="code-keyword">def</span> <span class="code-func">greet</span>(<span class="code-func">name</span>):
    <span class="code-keyword">return</span> <span class="code-str">"Hello, "</span> + name

<span class="code-keyword">print</span>(<span class="code-func">greet</span>(<span class="code-str">"Divyanshu"</span>))
    </code></pre>
    <h2 id= "installation">Installation</h2>
    <pre><code>pip install pythonaibrain == <span class = "code-num">1.0.2</span></code></pre>
    <br>
    <hr>
    <h2 id="modules">Modules</h2>
    <li><a href="#Camera">Camera</a></li>
    <li><a href="#TTS">TTS</a></li>
    <li><a href="#STT">STT</a></li>
    <li><a href="#TTI">TTI</a></li>
    <li><a href="#ITT">ITT</a></li>
    <li><a href="#Context">Context</a></li>
    <li><a href="#Brain">Brain</a></li>
    <li><a href="#AdvanceBrain">Advance Brain</a></li>
    <h3 id="Camera">Camera</h3>
    <article>PyAI supports Camera to click photos and make videos, it can save photos or videos and also send Images and Videos to PyAI to take answer.</article>
    <h4>Example</h4>
    <pre><code><span class="code-keyword">import </span>pyai
<span class="code-keyword">from</span> pyai <span class="code-keyword">import </span>Camera
<span class="code-keyword">import</span> tkinter <span class="code-keyword">as </span>tk

root = tk.Tk()
camera = <span class="code-class">Camera</span>(root)
root.mainloop()</code></pre>

    <h3 id="TTS">TTS</h3>
    <article>PyAI supports TTS to convert text to speech, it can also save the audio file.</article>
    <h4>Example</h4>
    <pre><code><span class="code-keyword">import </span>pyai

  </main>

  <footer>
    <p>&copy; 2025 PythonAI Brain. All rights reserved.</p>
  </footer>
</body>
</html>
'''

@app.route('/company')
def company():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>World Of Programming And Technology</title>
  <link rel="stylesheet" href="style.css" />
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      overflow-x: hidden;
      background: transparent;
    }

    spline-viewer.robot-3d {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: -1;
    }

    .content {
      position: relative;
      z-index: 1;
      padding: 2rem;
    }

    .floating-text {
      animation: float 4s ease-in-out infinite;
    }

    @keyframes float {
      0% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
      100% { transform: translateY(0); }
    }

    .animate-up {
      animation: rise 1.5s ease-out;
    }

    @keyframes rise {
      0% { opacity: 0; transform: translateY(20px); }
      100% { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
      opacity: 0;
      animation: fadeIn 2s ease forwards;
    }

    @keyframes fadeIn {
      0% { opacity: 0; }
      100% { opacity: 1; }
    }

    .scale-up {
      animation: scaleUp 1s ease forwards;
    }

    @keyframes scaleUp {
      0% { transform: scale(0.8); opacity: 0; }
      100% { transform: scale(1); opacity: 1; }
    }

    .slide-in-left {
      animation: slideLeft 1.5s ease-out;
    }

    @keyframes slideLeft {
      0% { transform: translateX(-100px); opacity: 0; }
      100% { transform: translateX(0); opacity: 1; }
    }

    .dark-toggle {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 2;
      background: rgba(0,0,0,0.6);
      color: #fff;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 20px;
      cursor: pointer;
    }

    .glass {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 10px;
      padding: 1rem;
    }

    .flip-card {
      background-color: transparent;
      width: 200px;
      height: 200px;
      perspective: 1000px;
      display: inline-block;
      margin: 1rem;
      animation: scaleUp 1s ease forwards;
    }

    .flip-card-inner {
      position: relative;
      width: 100%;
      height: 100%;
      text-align: center;
      transition: transform 0.6s;
      transform-style: preserve-3d;
    }

    .flip-card:hover .flip-card-inner {
      transform: rotateY(180deg);
    }

    .flip-card-front, .flip-card-back {
      position: absolute;
      width: 100%;
      height: 100%;
      backface-visibility: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
    }

    .flip-card-front {
      background-color: #222;
      color: white;
    }

    .flip-card-back {
      background-color: #555;
      color: white;
      transform: rotateY(180deg);
    }

    footer {
      text-align: center;
      margin-top: 2rem;
      color: white;
      animation: fadeIn 2s ease forwards;
    }

    .social-icons {
      margin: 1rem 0;
    }

    .icon {
      color: white;
      margin: 0 0.5rem;
      transition: transform 0.3s;
    }

    .icon:hover {
      transform: scale(1.2);
    }

    body.dark-mode {
      background-color: #111;
      color: white;
    }
  </style>
</head>
<body>
  <spline-viewer class="robot-3d" url="https://prod.spline.design/A7kM-EXRqh14Wo-q/scene.splinecode"></spline-viewer>
  <script type="module" src="https://unpkg.com/@splinetool/viewer@1.9.82/build/spline-viewer.js"></script>

  <div class="content">
    <button id="darkToggle" class="dark-toggle">🌙 Dark Mode</button>

    <header class="fade-in">
      <h1 class="floating-text">World Of Programming And Technology</h1>
      <p class="animate-up">Empowering Innovation Through Code</p>
    </header>

    <section class="about slide-in-left glass">
      <h2>About Us</h2>
      <p>We are a tech-driven company specializing in software development, AI, web technologies, and educational tools. Our mission is to make technology accessible and empowering for all.</p>
    </section>

    <section class="services animate-up">
      <h2 class="scale-up">Services</h2>
      <div class="flip-card">
        <div class="flip-card-inner">
          <div class="flip-card-front">
            <h3>Web Development</h3>
          </div>
          <div class="flip-card-back">
            <p>We build stunning websites and apps.</p>
          </div>
        </div>
      </div>
      <div class="flip-card">
        <div class="flip-card-inner">
          <div class="flip-card-front">
            <h3>AI Solutions</h3>
          </div>
          <div class="flip-card-back">
            <p>Advanced artificial intelligence tailored to your needs.</p>
          </div>
        </div>
      </div>
    </section>
    <section class="slide-in-left glass">
      <h2>Our Mission</h2>
      <p>We strive to harness the power of advanced technologies to solve real-world problems. Through innovation, research, and ethical development, we empower individuals and organizations to create a smarter future.</p>
    </section>

    <section class="scale-up glass">
    <div>
      <h2>Core Values</h2>
      <ul>
        <li>🌟 Integrity in Innovation</li>
        <li>🌍 Inclusive and Open Development</li>
        <li>🤝 User-Centric Design and Trust</li>
        <li>📈 Continuous Learning and Growth</li>
        <li>🧠 Ethical Use of AI</li>
      </ul>
    </div>
    </section>


    <footer class="fade-in">
      <p>Connect with us:</p>
      <div class="social-icons">
        <a href="https://github.com/World-Of-Programming-And-Technology" class="icon" aria-label="GitHub">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.73.5.5 5.74.5 12.02c0 5.1 3.29 9.42 7.86 10.96.58.1.79-.25.79-.56 0-.28-.01-1.02-.01-2-3.2.7-3.88-1.54-3.88-1.54-.53-1.35-1.3-1.7-1.3-1.7-1.06-.72.08-.7.08-.7 1.18.08 1.8 1.2 1.8 1.2 1.04 1.8 2.72 1.28 3.39.98.1-.76.4-1.28.73-1.57-2.56-.29-5.26-1.28-5.26-5.7 0-1.26.45-2.3 1.2-3.11-.12-.29-.52-1.46.11-3.04 0 0 .98-.31 3.2 1.19a11.2 11.2 0 0 1 5.84 0c2.22-1.5 3.2-1.19 3.2-1.19.63 1.58.23 2.75.11 3.04.75.81 1.2 1.85 1.2 3.11 0 4.43-2.7 5.4-5.27 5.68.41.36.77 1.08.77 2.18 0 1.57-.01 2.84-.01 3.22 0 .31.21.67.8.55A10.52 10.52 0 0 0 23.5 12c0-6.28-5.23-11.5-11.5-11.5z"/></svg>
        </a>
      </div>
      <p>&copy; 2025 World Of Programming And Technology</p>
    </footer>
  </div>

  <script>
    document.getElementById('darkToggle').addEventListener('click', () => {
      document.body.classList.toggle('dark-mode');
    });
  </script>
</body>
</html>
'''

@app.route('/pyai')
def pyai():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>World Of Programming And Technology</title>
  <link rel="stylesheet" href="style.css" />
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      overflow-x: hidden;
      background: transparent;
    }

    spline-viewer.robot-3d {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: -1;
    }

    .content {
      position: relative;
      z-index: 1;
      padding: 2rem;
    }

    .floating-text {
      animation: float 4s ease-in-out infinite;
    }

    @keyframes float {
      0% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
      100% { transform: translateY(0); }
    }

    .animate-up {
      animation: rise 1.5s ease-out;
    }

    @keyframes rise {
      0% { opacity: 0; transform: translateY(20px); }
      100% { opacity: 1; transform: translateY(0); }
    }

    .fade-in {
      opacity: 0;
      animation: fadeIn 2s ease forwards;
    }

    @keyframes fadeIn {
      0% { opacity: 0; }
      100% { opacity: 1; }
    }

    .scale-up {
      animation: scaleUp 1s ease forwards;
    }

    @keyframes scaleUp {
      0% { transform: scale(0.8); opacity: 0; }
      100% { transform: scale(1); opacity: 1; }
    }

    .slide-in-left {
      animation: slideLeft 1.5s ease-out;
    }

    @keyframes slideLeft {
      0% { transform: translateX(-100px); opacity: 0; }
      100% { transform: translateX(0); opacity: 1; }
    }

    .dark-toggle {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 2;
      background: rgba(0,0,0,0.6);
      color: #fff;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 20px;
      cursor: pointer;
    }

    .glass {
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 10px;
      padding: 1rem;
    }

    .flip-card {
      background-color: transparent;
      width: 200px;
      height: 200px;
      perspective: 1000px;
      display: inline-block;
      margin: 1rem;
      animation: scaleUp 1s ease forwards;
    }

    .flip-card-inner {
      position: relative;
      width: 100%;
      height: 100%;
      text-align: center;
      transition: transform 0.6s;
      transform-style: preserve-3d;
    }

    .flip-card:hover .flip-card-inner {
      transform: rotateY(180deg);
    }

    .flip-card-front, .flip-card-back {
      position: absolute;
      width: 100%;
      height: 100%;
      backface-visibility: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
    }

    .flip-card-front {
      background-color: #222;
      color: white;
    }

    .flip-card-back {
      background-color: #555;
      color: white;
      transform: rotateY(180deg);
    }

    footer {
      text-align: center;
      margin-top: 2rem;
      color: white;
      animation: fadeIn 2s ease forwards;
    }

    .social-icons {
      margin: 1rem 0;
    }

    .icon {
      color: white;
      margin: 0 0.5rem;
      transition: transform 0.3s;
    }

    .icon:hover {
      transform: scale(1.2);
    }

    body.dark-mode {
      background-color: #111;
      color: white;
    }

    .chat-toggle {
      position: fixed;
      bottom: 20px;
      right: 20px;
      z-index: 3;
      background: #0088cc;
      color: white;
      border: none;
      border-radius: 50%;
      width: 60px;
      height: 60px;
      font-size: 30px;
      cursor: pointer;
    }

    .chat-box {
      position: fixed;
      bottom: 90px;
      right: 20px;
      width: 300px;
      max-height: 400px;
      background: rgba(255, 255, 255, 0.95);
      border-radius: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.3);
      overflow: hidden;
      display: none;
      flex-direction: column;
      z-index: 3;
    }

    .chat-header {
      background: #0088cc;
      color: white;
      padding: 10px;
      font-weight: bold;
    }

    .chat-body {
      flex: 1;
      padding: 10px;
      overflow-y: auto;
    }

    .chat-input {
      display: flex;
      border-top: 1px solid #ccc;
    }

    .chat-input input {
      flex: 1;
      border: none;
      padding: 10px;
    }

    .chat-input button {
      background: #0088cc;
      color: white;
      border: none;
      padding: 10px 15px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <spline-viewer class="robot-3d" url="https://prod.spline.design/A7kM-EXRqh14Wo-q/scene.splinecode"></spline-viewer>
  <script type="module" src="https://unpkg.com/@splinetool/viewer@1.9.82/build/spline-viewer.js"></script>

  <div class="content">
    <button id="darkToggle" class="dark-toggle">🌙 Dark Mode</button>

    <header class="fade-in">
      <h1 class="floating-text">World Of Programming And Technology</h1>
      <p class="animate-up">Empowering Innovation Through Code</p>
    </header>

    <section class="about slide-in-left glass">
      <h2>About Us</h2>
      <p>We are a tech-driven company specializing in software development, AI, web technologies, and educational tools. Our mission is to make technology accessible and empowering for all.</p>
    </section>

    <section class="services animate-up">
      <h2 class="scale-up">Services</h2>
      <div class="flip-card">
        <div class="flip-card-inner">
          <div class="flip-card-front">
            <h3>Web Development</h3>
          </div>
          <div class="flip-card-back">
            <p>We build stunning websites and apps.</p>
          </div>
        </div>
      </div>
      <div class="flip-card">
        <div class="flip-card-inner">
          <div class="flip-card-front">
            <h3>AI Solutions</h3>
          </div>
          <div class="flip-card-back">
            <p>Advanced artificial intelligence tailored to your needs.</p>
          </div>
        </div>
      </div>
    </section>

    <footer class="fade-in">
      <p>Connect with us:</p>
      <div class="social-icons">
        <a href="https://github.com/" class="icon" aria-label="GitHub">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.73.5.5 5.74.5 12.02c0 5.1 3.29 9.42 7.86 10.96.58.1.79-.25.79-.56 0-.28-.01-1.02-.01-2-3.2.7-3.88-1.54-3.88-1.54-.53-1.35-1.3-1.7-1.3-1.7-1.06-.72.08-.7.08-.7 1.18.08 1.8 1.2 1.8 1.2 1.04 1.8 2.72 1.28 3.39.98.1-.76.4-1.28.73-1.57-2.56-.29-5.26-1.28-5.26-5.7 0-1.26.45-2.3 1.2-3.11-.12-.29-.52-1.46.11-3.04 0 0 .98-.31 3.2 1.19a11.2 11.2 0 0 1 5.84 0c2.22-1.5 3.2-1.19 3.2-1.19.63 1.58.23 2.75.11 3.04.75.81 1.2 1.85 1.2 3.11 0 4.43-2.7 5.4-5.27 5.68.41.36.77 1.08.77 2.18 0 1.57-.01 2.84-.01 3.22 0 .31.21.67.8.55A10.52 10.52 0 0 0 23.5 12c0-6.28-5.23-11.5-11.5-11.5z"/></svg>
        </a>
      </div>
      <p>&copy; 2025 World Of Programming And Technology</p>
    </footer>
  </div>

  <!-- AI Chatbot Elements -->
  <button class="chat-toggle" onclick="toggleChat()">💬</button>
  <div class="chat-box" id="chatBox">
    <div class="chat-header">AI Assistant</div>
    <div class="chat-body" id="chatBody"></div>
    <div class="chat-input">
      <input type="text" id="userInput" placeholder="Ask something..." />
      <button onclick="sendMessage()">Send</button>
    </div>
  </div>

  <script>
    document.getElementById('darkToggle').addEventListener('click', () => {
      document.body.classList.toggle('dark-mode');
    });

    function toggleChat() {
      const box = document.getElementById('chatBox');
      box.style.display = box.style.display === 'flex' ? 'none' : 'flex';
    }

    function sendMessage() {
      const input = document.getElementById('userInput');
      const body = document.getElementById('chatBody');
      const userText = input.value.trim();
      if (userText === '') return;

      body.innerHTML += `<div><strong>You:</strong> ${userText}</div>`;

      setTimeout(() => {
        const response = getAIResponse(userText);
        body.innerHTML += `<div><strong>AI:</strong> ${response}</div>`;
        body.scrollTop = body.scrollHeight;
      }, 500);

      input.value = '';
    }

    function getAIResponse(text) {
      if (text.toLowerCase().includes('hello')) return 'Hi there! How can I assist you today?';
      if (text.toLowerCase().includes('your name')) return "I'm your virtual AI assistant!";
      return "I'm still learning. Try asking something else!";
    }
  </script>
</body>
</html>
'''
brain = Brain()
brain.load()
@app.route("/PyAI", methods=["POST"])
def PyAI():
    user_msg = request.json.get("message")
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400
    
    bot_reply = brain.process_messages(user_msg)  # AI logic here
    return jsonify({"response": bot_reply})


@app.route('/api/<string:n>')
def check(n):
    pass

class Server:
    def __init__(self, debug: bool | None = False, host: str | None = '127.0.0.1', port: int | None = 8080) -> None:
        self.debug = debug
        self.host = host
        self.port = port

    def run(self) -> None:
        app.run(debug= self.debug, port= self.port, host= self.host)
        return None

# https://nextjs-ai-chatbot-flame-eight-56.vercel.app/chat/034a89cf-36fa-4595-8df0-71bb214e81b7
if __name__ == '__main__':
    app.run(debug = False, port=port, host= host)

__all__ = [
    "Server",
    "app"
]

__version__ = '1.0.8'
