# Monkey patching (fold)

class Hash
  def method_missing(sym,*args)
    fetch(sym){fetch(sym.to_s){super}}
  end
  def id
    fetch(:id){fetch('id'){raise}}
  end
end

class String
  def exist?
    File.exist?(self)
  end
end
  

module Enumerable
  def fmap#{|each|}
    ary=[];each{|each|ary.concat(yield(each))};ary
  end
  def count_by
    h = Hash.new(0)
    each{|each|h[yield(each)]+=1}
    h.sort_by{|k,count|count}.reverse
  end
  def split_where # {|a,b|}
    runs = [[first]]
    each_cons(2){|a,b|
      runs << [] if yield(a,b)
      runs.last << b
    }
    return runs 
  end
  def any
    first
  end
  def sample
    shuffle.first
  end
  def average
    inject(&:+) / size
  end
  def sum
    inject(&:+)
  end
  def percentile(f)
    raise "Expecting value between 0.0 and 1.0!" if f > 1
    return nil if empty?
    sorted = self.sort
    n = f.to_f * (self.size - 1)
    a,b = n.floor,n.ceil
    return sorted[a] if a == b
    (b-n) * sorted[a] + (n-a) * sorted[b]
  end
  def as_hash
    h = Hash.new(0)
    each{|each|h[yield(each)]=each}
    return h
  end
end

class Array
  def but_last
    self[0...-1]
  end
end

def parse_time(str)
  Time.utc(*str.scan(/\d+/).collect(&:to_i))
end

# A poor man's testing framework

class Should
  def initialize(value)
    @value = value
  end
  def ==(expected)    
    raise "Found #{@value.inspect} but expected #{expected.inspect}" unless @value == expected
  end
end

class Object
  def should
    Should.new(self)
  end
  def should_s
    Should.new(self.to_s)
  end
end

# (end)

if $0 == __FILE__ then
  1.should == 1
  
  # Hash.method_missing hack
  
  {:hello=>'world'}.hello.should == 'world'
  {:id=>23}.id.should == 23
  
  # Array.but_last
  
  [1,2,3].but_last.should == [1,2]
  
  # Describtive statistics
  
  [1,2,3.3,3.4,4,5].sum.should == 18.7
  [1,2,3.3,3.4,4,5].average.should_s == '3.11666666666667'
  
  # Percentile, you darn beast!
  
  [1,2,3,4,5].percentile(0.25).should == 2
  [1,2,3,4,5].percentile(0.75).should == 4
  [1,2,3,4].percentile(0.5).should == 2.5
  [1,2].percentile(0.25).should == 1.25
  
end