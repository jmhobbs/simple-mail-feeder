# -*- coding: utf-8 -*-

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mailer:

	def __init__ ( local = False, host = None, port = 25 ):
		self.local = local
		self.host = host
		self.port = port

	def send ( send_to, send_from ):
		if self.local:
			self.local( send_to, send_from )
		else:
			self.smtp( send_to, send_from )

	def smtp ( send_to, send_from ):
		msg = MIMEMultipart( 'alternative' )
		msg[ 'Subject' ] = "Link"
		msg[ 'From' ] = send_from
		msg[ 'To' ] = send_to

		text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttp://www.python.org"

		html = """\
<html>
	<head></head>
	<body>
		<p>Hi!<br>
			How are you?<br>
			Here is the <a href="http://www.python.org">link</a> you wanted.
		</p>
	</body>
</html>
"""

		part1 = MIMEText( text, 'plain' )
		part2 = MIMEText( html, 'html' )

		msg.attach( part1 )
		msg.attach( part2 )

		if None != self.host:
			s = smtplib.SMTP( self.host, self.port )
		else:
			s = smtplib.SMTP()
		s.sendmail( send_from, send_to, msg.as_string() )
		s.quit()

	def sendmail ():
		sendmail_location = "/usr/sbin/sendmail" # sendmail location
		p = os.popen("%s -t" % sendmail_location, "w")
		p.write("From: %s\n" % "from@somewhere.com")
		p.write("To: %s\n" % "to@somewhereelse.com")
		p.write("Subject: thesubject\n")
		p.write("\n") # blank line separating headers from body
		p.write("body of the mail")
		status = p.close()
		if status != 0:
			print "Sendmail exit status", status