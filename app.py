from flask import Flask, render_template, request, redirect, session, url_for,flash,Response
import scrape
import sentiment_analysis
app = Flask(__name__)
app.secret_key="whats up"
#image=Images(app)

@app.route("/")
def main():
   return render_template('index.html')

@app.route('/getStarted')
def starting():
    return render_template('started.html')

@app.route('/appSearch', methods=['POST','GET'])
def appsearch():
   if request.method == 'GET':
      return render_template('search.html')
   elif request.method == 'POST':
      search_tb= request.form['sr']
      session['app_name']=search_tb
      if(session['app_name'].isdigit()):
         flash("Invalid input")
      
      return redirect(url_for('search_result'))

@app.route('/searchResult', methods=['POST','GET'])
def search_result():
   aname=session['app_name']
   
   
   try:
      res,result=scrape.search(aname)
      res=scrape.app_details(result)
      return render_template('searchResult.html', name =res)
   except AttributeError:
      error='Invalid App Name'
      return render_template('searchResult.html', error =error)
   


@app.route('/similarApp', methods=['POST','GET'])
def appsimilar():
   #session['appname'] = 0
   if request.method == 'GET':
      return render_template('similar.html')
   elif request.method == 'POST':
      searchtb= request.form['tb']
      session['appname']=searchtb
      return redirect(url_for('similar_result'))

@app.route('/similarResult', methods=['POST','GET'])
def similar_result():
   anme=session['appname']
   
   try:
      rest,results=scrape.search(anme)
      rest=scrape.SimilarApps(results)
      return render_template('similarResult.html', name =rest)
      #print res
   except AttributeError:
      error='Invalid App Name'
      return render_template('similarResult.html', error=error)

@app.route('/topApp', methods=['POST','GET'])
def top_app():
   if request.method == 'GET':
      return render_template('topapp.html')
   elif request.method == 'POST':
      searcht= request.form['cat']
      session['ppname']=searcht
      return redirect(url_for('top_result'))
   
@app.route('/appResult', methods=['POST','GET'])
def top_result():
   category=''
   n='0'
   anme=session['ppname']
   if(anme=='Education : New & Updated Apps'):
      category='EDUCATION'
      n='1'
   if(anme=='Education : Learn to Code'):
      category='EDUCATION'
      n='2'
   if(anme=='Education : Study Aids & Prep'):
      category='EDUCATION'
      n='3'
   if(anme=='Education : Speak a New Language'):
      category='EDUCATION'
      n='4'
   if(anme=='Social : Blogs,Forms & More'):
      category='SOCIAL'
      n='1'
   if(anme=='Social : Video & Photo Sharing'):
      category='SOCIAL'
      n='2'
   if(anme=='Social : Connect with friends'):
      category='SOCIAL'
      n='3'
   if(anme=='Social : Messaging Apps'):
      category='SOCIAL'
      n='4'
   if(anme=='Lifestyle : Latest Fitness Apps'):
      category='LIFESTYLE'
      n='1'
   if(anme=='Lifestyle : Apps for Styling'):
      category='LIFESTYLE'
      n='2'
   if(anme=='Lifestyle : Stress Relief Apps'):
      category='LIFESTYLE'
      n='3'
   if(anme=='Lifestyle : Do-It-Yourself'):
      category='LIFESTYLE'
      n='4'
   if(anme=='Action Games'):
      category='GAME_ACTION'
      n='0'
   if(anme=='Adventure Games'):
      category='GAME_ADVENTURE'
      n='0'
   if(anme=='Arcade Games'):
      category='GAME_ARCADE'
      n='0'
   try:
      resty=scrape.top_App(category,n)
      return render_template('topresult.html', name =resty)
   except AttributeError():
      error='Invalid App Name'
      return render_template('topresult.html', error=error)
      

@app.route('/appCompare', methods=['POST','GET'])
def comparing():
   if request.method == 'GET':
      return render_template('compare.html')
   elif request.method == 'POST':
      comparetb1 = request.form['tb1']
      comparetb2 = request.form['tb2']
      session['appname1']=comparetb1
      session['appname2']=comparetb2
      return redirect(url_for('compare_result'))

@app.route('/compareResult', methods=['POST','GET'])
def compare_result():
   
   anme1=session['appname1']
   anme2=session['appname2']
   try:
      app1,app2,neu1,pos1,neg1,neu2,pos2,neg2=sentiment_analysis.scrp(anme1,anme2)
   
      if app1>app2:
         flash(str(anme1).upper()+' is better')
      else:
         flash(str(anme2).upper()+' is better')
      import pygal
      pie_chart = pygal.Pie()
      pie_chart.title = ' TOP REVIEWS FOR '+str(anme1).upper()
      pie_chart.add('NEGATIVE', neg1)
      pie_chart.add('POSITIVE', pos1)
      pie_chart.add('NEUTRAL', neu1)
      pie_chart.render_to_file('pie_chart1.svg')
      pie_chart2 = pygal.Pie()
      pie_chart2.title = 'TOP REVIEWS FOR '+str(anme2).upper()
      pie_chart2.add('NEGATIVE', neg2)
      pie_chart2.add('POSITIVE', pos2)
      pie_chart2.add('NEUTRAL', neu2)
      pie_chart2.render_to_file('pie_chart2.svg')
      graph_data1 = pie_chart.render_data_uri()
      graph_data2 = pie_chart2.render_data_uri()
      return render_template("compareResult.html", graph_data1 = graph_data1,graph_data2=graph_data2)
   except AttributeError:
      error='Invalid App Name'
      return render_template('compareResult.html', error=error)
   #return Response(response=pie_chart.render(), content_type='image/svg+xml')   

if __name__ == '__main__':
   app.run(debug=True)
