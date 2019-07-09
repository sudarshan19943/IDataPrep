import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { DataService } from '../data.service';

@Component({
  selector: 'app-csv-file-download',
  templateUrl: './csv-file-download.component.html',
  styleUrls: ['./csv-file-download.component.scss']
})
export class CsvFileDownloadComponent implements OnInit {

  @Output() completed = new EventEmitter<boolean>();
  ready = false;

  constructor(private dataservice: DataService) { }

  ngOnInit() {
    this.dataservice.cleanedFileReady.subscribe(data => {
      // do awesome stuff with data
      this.ready = true;
    });
  }

  downloadFile() {
    this.completed.emit(true);
  }
}
