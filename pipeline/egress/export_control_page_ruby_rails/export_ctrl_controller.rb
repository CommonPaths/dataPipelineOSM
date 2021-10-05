class ExportCtrlController < ApplicationController
  require 'open3'
  skip_authorization_check
  skip_before_action :verify_authenticity_token

  def export_page
  end

  def download_osc
   now_date_time = Time.now.strftime("%F_%H_%M")
   filename_download = "pr_noPII_export_" + now_date_time + ".osc"
   send_file(
    "#{Rails.root}/public/pr_noPII_export.osc",
    filename: filename_download,
    type: "application/pdf"
   )
   @formstring = '.'
  end

   def button
    cmd_foldername = ENV["FOLDERNAME_PR_EXPORT"]
    if cmd_foldername.nil? || cmd_foldername.empty?
      cmd_foldername = '/home/ubuntu/pr_export/'
    end
    cmd_filename = 'export_pr_changeset.sh'
    cmd = cmd_foldername + cmd_filename
    script_out_err = ''
    @formstring = 'Processing ...'
    Open3.popen2e(cmd) do |stdin, stdout_err, wait_thr|
      script_out_err = stdout_err.read + script_out_err
      status_code = wait_thr.value
      status_value = "Export Script Run Success = " + (status_code.success?).to_s 
      puts script_out_err + status_value
      @formstring = script_out_err + status_value
    end
  end

end
