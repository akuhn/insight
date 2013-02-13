require 'rubygems'
require 'mongo'
require 'json'

# Save graph and sights to json files

def export(database)
  db = Mongo::MongoClient.new()[database]
  %w{ sights graph }.each do |name|
    puts "Backing up #{name}..."
    File.open("mongo-backup-#{name}.json",'w') do |f|
      db[name].find.each do |each|
        each.delete('_id')
        f.puts(JSON.dump(each))
      end
    end
  end
end

def import(database)
  db = Mongo::MongoClient.new()[database]
  %w{ sights graph }.each do |name|
    puts "Reading up #{name}..."
    coll = db[name]
    File.open("mongo-backup-#{name}.json").each do |each|
      p JSON.parse(each)
      coll.insert(JSON.parse(each))
    end
  end
end

print 'import or export'

