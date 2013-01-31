require 'rubygems'
require 'open-uri'
require 'nokogiri'
require 'mongo'
require 'json'
require 'pry'

require 'monkey_patching'

def download_webpages!
  # download websites and store them in /data
  url = 'http://www.lonelyplanet.com/italy/rome/things-to-do'
  url = 'http://www.lonelyplanet.com/france/paris/things-to-do'
  url = 'http://www.lonelyplanet.com/usa/san-francisco/things-to-do'
  url = 'http://www.lonelyplanet.com/canada/vancouver/things-to-do'
  loop do
    p url
    p fname = 'data/' << url.gsub(/\W+/,'-') << '.html'
    html = open(url).read
    File.open(fname,'w'){|f|f.write(html)}
    doc = Nokogiri::HTML(html)
    url = 'http://www.lonelyplanet.com' << doc.at('a.next')['href']
  end
end

def scrape_points_of_interest!
  # scrape point of interest into mongodb
  mongo = Mongo::MongoClient.new()
  db = mongo['4h']
  __points__ = db['poi']
  Dir.glob('data/*lonelyplanet*vancouver*.html') do |each|
    doc = Nokogiri::HTML(File.read(each))
    locations = JSON.parse(doc.search('head script').last.content[/\[\{.*\}\]/])
    doc.search('ol > li').each do |li|
      next if li['class'] == 'advertisingItem'
      p data = {
        :name => li.at('h2 a').content,
        :url => 'http://www.lonelyplanet.com' << li.at('h2 a')['href'],
        :category => li.search('.poiType a')[0]['href'].split('/')[-1],
        :subcategory => li.search('.poiType a')[1]['href'].split('/')[-1],
        :location => li.search('.poiLocation a').collect{|m|m['href'].split('/')[-2]},
        :description => li.at('.listDesc p').content,
        :reviewed => !!li.at('.reviewed'),
        :thumbs => { 
          :up => li.at('.thumbs .up').content.to_i,
          :down => li.at('.thumbs .down').content.to_i
        }
      }
      more = locations.detect{|m|m.name == data.name}
      raise binding.pry unless more
      data.update(
        :latitude => more.latitude,
        :longitude => more.longitude
      )
      __points__.insert(data)
    end
  end
end

# scrape_points_of_interest!
