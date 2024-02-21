using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace CSCI3280_GP_Project
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();

            //Set Default to 1x
            playSpeedDropDown.SelectedIndex = 2;

            //For testing
            for (int i = 0; i < 100; i++) 
            {
                Button button = new Button();
                button.Text = i.ToString();
                button.MouseDown += new MouseEventHandler(this.ButtonClick);

                recordingContents.Controls.Add(button);
            }

            
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void recordingContents_Paint(object sender, PaintEventArgs e)
        {

        }

        private void recordingButton_Click(object sender, EventArgs e)
        {

        }

        private void playButton_Click(object sender, EventArgs e)
        {

        }
        

        private void playSpeedDropDown_SelectedIndexChanged(object sender, EventArgs e)
        {

        }



        //For testing
        public void ButtonClick(object sender, MouseEventArgs e)
        {
            if (e.Button == MouseButtons.Left)
            {
                timeDetails.Text = "Left";
            }
            if (e.Button == MouseButtons.Right)
            {
                timeDetails.Text = "Right";
            }
        }
    }
}
