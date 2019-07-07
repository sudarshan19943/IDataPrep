import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-csv-file-upload',
  templateUrl: './csv-file-upload.component.html',
  styleUrls: ['./csv-file-upload.component.scss']
})
export class CsvFileUploadComponent implements OnInit {

  @Input() forClassification;
  @Output() forClassificationChanged = new EventEmitter<boolean>();
  @Output() completed = new EventEmitter<boolean>();
  hasHeader = true;
  filename = '';
  constructor() { }

  ngOnInit() {
  }

  onFileInput(event: any) {
    this.filename = 'Selected Filename: ' + event.target.files[0].name;
  }

  sendFile() {
    console.log('Sending File');
    this.completed.emit(true);
  }

  test(){
    console.log(this.hasHeader);
  }

}
