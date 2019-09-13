# Build a Flask/ExpressJS Webserver

## Purpose
To get Data Engineers at LeanTaaS to build a webserver that follows the restful convention.
My goal here is to just to introduce some concepts with simplified explainations.

## Part 1 - Reading (15 minutes)

#### What is HTTP
HTTP is a protocol based off of TCP/IP.

Think of TCP/IP as a messenger that can transport binary information across a network.
It will take a file, split it up into multiple small parts (packets), and throw it over
the wire. When each packet reaches its destination, the machine that received the packet will
send back a confirmation saying "hey, I got this packet". If the sender doesn't receive this
confirmation, it will send the packet over the wire again until either the receiver gets the packet
or a timeout occurs.

HTTP uses TCP/IP to relay information from the client to the server, and back. In our analogy, if
TCP/IP is the messenger, then HTTP is the format of the message. Each message consists of a `start-line`,
a `header`, and (optionally) a `body` (we'll get into that later).

Let's just say that the client (your computer at home) wants to contact a server (a computer in the cloud).
HTTP is the protocol that governs the rules of this engagement. There are two messages that get sent back and forth:
the request and the response. The request starts off from the client and goes to the server, and the
response works vice-versa. The request and response messages share the same message format, but will
have different start-lines/headers. So if we're contacting leantaas.com through our browser, our request will ask leantaas.com
for a GET request with no headers and no body. I pasted the response below. The Header says, hey this message
is in HTTPv2.0, and your status came back as success (HTTP code 200). There's a body attached to this message that's
26KBs in size, and the type of the message is utf-8 text in the format of HTML. The browser gets this response and knows
to render out the HTML directly to the user - hence you get the webpage for leantaas.com!

```HTTP/2.0 200 OK
cache-control: public, max-age=600
content-encoding: gzip
content-type: text/html; charset=UTF-8
server: nginx
date: Thu, 12 Sep 2019 16:22:15 GMT
vary: Accept-Encoding, Cookie, Cookie
age: 20
accept-ranges: bytes
via: 1.1 varnish
content-length: 26615
```


#### Format of An HTTP Message
* The `start-line` has an
    * The *HTTP-VERSION* is exactly what is sounds like: the version of HTTP that you're using. Most of the internet still
    runs on v1.1, but in 2015 v2.0 was approved by the Internet Engineering Task Force (IETF) as a standard.
    * *HTTP-METHOD* which is like a verb that tells the server what you're doing (i.e: GET, POST, PUT, OPTIONS, etc.). To put this into context,
    when you put in an address like www.leantaas.com into your browser, your browser is making a GET
    request to the leantaas servers.
    * (request-message-specific) The *request target* are usually the URL you are trying to contact. URLs are converted into IP Address.
    through a process called Domain Name System (DNS) Lookup, but we won't get into that today.
    * (response-message-specific) The *HTTP status code* is the an integer that states the status of the request. Codes in the 200s
    means success, 300s means redirects, 400s means client errors (i.e: 404 Page not found). 500s means server errors (as in your webserver crashed).
    [Here's a lst of status codes and their meaning. Error Code #418 is my favorite](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
* The `header` is like a dictionary of key-value pairs. The standard headers will describe the
message like *User-Agent*, *Accept-Language*, and *Content-Length* (which describes the body below). Some
headers will tell the browser to behave in a certain way like "store this cookie" (*Set-Cookie*), or
"don't you dare cache this" (*Cache-Control*). Each header key does something specific. [Here's a list of them!](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)
* The `body` is finally what goes into your message. This can be text, or pure binary. It can be a JSON or
it can be a file. It can also be just a plain old HTML webpage. The body is optional. GET requests, for example,
don't have a body when making the request.

[More information can be found on MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages)

## Part 2 - Enough Talk, More Doing
We're going to be making a webserver using Flask. Flask is a really simple framework that basically translates HTTP requests
into python functions and back. It's pretty straight-forward which is why we're using it. If you like JS Flask works a lot
like ExpressJS. Other frameworks, such as Java Spring, Java Play, Ruby on Rails, MeteorJS, and python's Django use
variants of Model-View-Controller design pattern that have stronger constraints and differing opinions on how you should
write a webserver. However, the end-result is mostly the same: you have a thread listening in on a port that's ready to accept
HTTP requests and spit back HTTP responses.

Our app is a social network for cats. Cats post their names, gender, profile pictures, and their ages. We're going to be
Mark Zuckerberg... but with cats. We'll call our billion dollar website: `Fur Real`.  

1. Download Postman. Postman is a chrome extension that's going to help you make requests to our webserver.
2. Run app.py, your webserver is now listening in on localhost:5000. It's looking for requests.
3. Open your browser, go to http://localhost:5000. This sends a GET requests to your app and the server responds back 
   with a webpage. Now do the same with postman, you should see the same result. Unfortunately your browser can only send
   GET requests, which is why we need Postman.
4. You need a Database in order to store information about your cats. We could store transactions in a text file like a
   CSV, but that file might have bad data, get deleted, or corrupted! Databases are our friends, so we're going to use MySQL.
   Feel free to SQLLite or Postgres or whatever your comfortable with. Import the sql seed file into your db with the cmd
   ```bash
   mysql -u your_mysql_username -p < ./sql/seed.sql 
   ```
5. For flask go into the `flask` folder and run
    ```bash
    pip install -r requirements.txt
    python app.py
    ```
6. For Express go into the `express` folder and run
    ```bash
    npm i
    node app.js
    ```
5. Download Python 3.6 or higher and run the unit-tests in the flask folder. Good luck!
    ```bash
    # to run all tests
    python -m pytest api_tests.py
    # to run just one test
    python -m pytest api_tests.py::test_server_is_up
    ```
6. Pass all tests. Ask me if you need help. Good Luck