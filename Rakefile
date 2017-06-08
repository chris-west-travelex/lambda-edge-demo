require 'rspec/core/rake_task'

task :default => :spec

namespace :spec do
  targets = []
  Dir.entries('./roles/').each do |dir|
    next unless File.directory?("./roles/" + dir + "/spec") and not dir.start_with? '.'
    targets << dir
  end

  task :all     => targets
  task :default => :all

  targets.each do |target|
    desc "Run awspec tests for #{target}"
    RSpec::Core::RakeTask.new(target.to_sym) do |t|
      t.pattern = "./roles/#{target}/spec/*_spec.rb"
    end
  end
end
