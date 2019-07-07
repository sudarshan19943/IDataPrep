import { Component, OnInit, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-csv-file-download',
  templateUrl: './csv-file-download.component.html',
  styleUrls: ['./csv-file-download.component.scss']
})
export class CsvFileDownloadComponent implements OnInit {

  @Output() completed = new EventEmitter<boolean>();

  constructor() { }

  ngOnInit() {
  }

  downloadFile(){
    this.completed.emit(true);
  }
}
