namespace CSCI3280_GP_Project
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.recordingContents = new System.Windows.Forms.FlowLayoutPanel();
            this.recordingButton = new System.Windows.Forms.Button();
            this.playButton = new System.Windows.Forms.Button();
            this.timeDetails = new System.Windows.Forms.Label();
            this.playSpeedDropDown = new System.Windows.Forms.ComboBox();
            this.SuspendLayout();
            // 
            // recordingContents
            // 
            this.recordingContents.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left)));
            this.recordingContents.AutoScroll = true;
            this.recordingContents.BackColor = System.Drawing.Color.GreenYellow;
            this.recordingContents.Location = new System.Drawing.Point(12, 12);
            this.recordingContents.Name = "recordingContents";
            this.recordingContents.Size = new System.Drawing.Size(300, 805);
            this.recordingContents.TabIndex = 0;
            this.recordingContents.Paint += new System.Windows.Forms.PaintEventHandler(this.recordingContents_Paint);
            // 
            // recordingButton
            // 
            this.recordingButton.Anchor = System.Windows.Forms.AnchorStyles.Left;
            this.recordingButton.Font = new System.Drawing.Font("PMingLiU", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(136)));
            this.recordingButton.Location = new System.Drawing.Point(344, 680);
            this.recordingButton.Name = "recordingButton";
            this.recordingButton.Size = new System.Drawing.Size(180, 100);
            this.recordingButton.TabIndex = 1;
            this.recordingButton.Text = "Recording";
            this.recordingButton.UseVisualStyleBackColor = true;
            this.recordingButton.Click += new System.EventHandler(this.recordingButton_Click);
            // 
            // playButton
            // 
            this.playButton.Anchor = System.Windows.Forms.AnchorStyles.Right;
            this.playButton.Font = new System.Drawing.Font("PMingLiU", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(136)));
            this.playButton.Location = new System.Drawing.Point(1016, 680);
            this.playButton.Name = "playButton";
            this.playButton.Size = new System.Drawing.Size(180, 100);
            this.playButton.TabIndex = 2;
            this.playButton.Text = "Play";
            this.playButton.UseVisualStyleBackColor = true;
            this.playButton.Click += new System.EventHandler(this.playButton_Click);
            // 
            // timeDetails
            // 
            this.timeDetails.AutoSize = true;
            this.timeDetails.Font = new System.Drawing.Font("PMingLiU", 18F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(136)));
            this.timeDetails.Location = new System.Drawing.Point(550, 712);
            this.timeDetails.Name = "timeDetails";
            this.timeDetails.Size = new System.Drawing.Size(442, 48);
            this.timeDetails.TabIndex = 3;
            this.timeDetails.Text = "00:00:00.00 / 00:00:00";
            this.timeDetails.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // playSpeedDropDown
            // 
            this.playSpeedDropDown.FormattingEnabled = true;
            this.playSpeedDropDown.Items.AddRange(new object[] {
            "0.25x",
            "0.5x",
            "1x",
            "1.5x",
            "2x",
            "4x"});
            this.playSpeedDropDown.Location = new System.Drawing.Point(1239, 712);
            this.playSpeedDropDown.Name = "playSpeedDropDown";
            this.playSpeedDropDown.Size = new System.Drawing.Size(192, 32);
            this.playSpeedDropDown.TabIndex = 4;
            this.playSpeedDropDown.SelectedIndexChanged += new System.EventHandler(this.playSpeedDropDown_SelectedIndexChanged);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(13F, 24F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1574, 829);
            this.Controls.Add(this.playSpeedDropDown);
            this.Controls.Add(this.timeDetails);
            this.Controls.Add(this.playButton);
            this.Controls.Add(this.recordingButton);
            this.Controls.Add(this.recordingContents);
            this.Cursor = System.Windows.Forms.Cursors.Default;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.Name = "Form1";
            this.Text = "Sound Recorder";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.FlowLayoutPanel recordingContents;
        private System.Windows.Forms.Button recordingButton;
        private System.Windows.Forms.Button playButton;
        private System.Windows.Forms.Label timeDetails;
        private System.Windows.Forms.ComboBox playSpeedDropDown;
    }
}

